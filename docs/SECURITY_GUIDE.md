# 🔒 Guía de Seguridad - Sistema de Autenticación

## Estado Actual de Seguridad

### ✅ Implementado

| Característica | Estado | Descripción |
|---|---|---|
| Hasheo de contraseñas | ✅ | SHA256 (mejorable) |
| Control de acceso RBAC | ✅ | Roles admin/worker |
| Historial de auditoría | ✅ | Tabla session_assignments |
| Variables de entorno | ✅ | Credenciales protegidas |
| Soft delete de usuarios | ✅ | Los usuarios no se eliminan |
| Sesiones de usuario | ✅ | Cada sesión tiene dueño |
| Reasignación controlada | ✅ | Log de quién reasigna |

### ⚠️ En Producción (CRÍTICO)

1. **Cambiar contraseña de administrador**
   - Cambiar: `admin123` → Contraseña fuerte
   - Dónde: Ejecutar desde la aplicación "Mi Cuenta"

2. **Usar HTTPS obligatoriamente**
   - Configurar en servidor Streamlit
   - O usar reverse proxy (nginx)

3. **Mejorar hasheo de contraseñas**
   - Cambiar de SHA256 a bcrypt o argon2
   - Script de migración incluido

4. **Configurar backups automáticos**
   - Configurar PostgreSQL para backups
   - O usar herramientas como pg_dump

5. **Implementar 2FA (dos factores)**
   - Opcional pero recomendado
   - Email OTP o TOTP

---

## 🔐 Mejoras de Seguridad Implementables

### Opción 1: Mejorar Hasheo de Contraseñas (RECOMENDADO)

**Actual:** SHA256 (no seguro para contraseñas)
**Mejora:** bcrypt o argon2

```python
# Instalación
pip install bcrypt

# Modificar auth_manager.py
import bcrypt

def hash_password(self, password: str) -> str:
    """Usa bcrypt en lugar de SHA256"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(self, password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
```

---

### Opción 2: Implementar Rate Limiting

Previene ataques de fuerza bruta:

```python
# Instalar
pip install streamlit-rate-limit

# En login_interface.py
from streamlit_rate_limit import check_rate_limit

@check_rate_limit(max_calls=5, time_window=300)  # 5 intentos cada 5 min
def authenticate_user(username, password):
    # ...código de autenticación
```

---

### Opción 3: Agregar 2FA con Email OTP

```python
# Instalar
pip install pyotp qrcode

# Generar código OTP
import pyotp
import qrcode

def setup_2fa(user_email):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # Generar código QR
    uri = totp.provisioning_uri(user_email, issuer_name="Fonseca-Canaca")
    qr = qrcode.make(uri)
    
    return secret, qr

# Verificar código
def verify_2fa(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
```

---

### Opción 4: Encriptación de Datos Sensibles

```python
# Instalar
pip install cryptography

from cryptography.fernet import Fernet

# Generar clave (una sola vez)
key = Fernet.generate_key()  # Guardar en .env

# Encriptar datos sensibles
cipher = Fernet(key)
encrypted_data = cipher.encrypt(session_data.encode())

# Desencriptar
decrypted_data = cipher.decrypt(encrypted_data).decode()
```

---

## 📋 Checklist de Seguridad Pre-Producción

### Antes de lanzar a producción:

- [ ] Cambiar contraseña admin por una fuerte
- [ ] Cambiar ADMIN_PASSWORD en `.env`
- [ ] Configurar HTTPS/SSL
- [ ] Hacer backup de la BD
- [ ] Revisar y cambiar credenciales de PostgreSQL
- [ ] Mejorar hasheo de contraseñas (bcrypt)
- [ ] Implementar rate limiting
- [ ] Configurar firewall
- [ ] Restringir acceso a BD (localhost solo)
- [ ] Revisar permisos de archivos
- [ ] Eliminar .env.example
- [ ] Configurar logs
- [ ] Documentar procedimientos de recuperación
- [ ] Entrenar usuarios en seguridad
- [ ] Pruebas de penetración

---

## 🔑 Gestión de Credenciales

### Variables de Entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña_fuerte@servidor:5432/db

# Admin (cambiar en producción)
ADMIN_PASSWORD=contraseña_fuerte_aleatorias_caracteres_2024

# Opcional: Clave para encriptación
ENCRYPTION_KEY=clave_generada_aleatoria_base64

# Opcional: Configuración de email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=contraseña_aplicacion
```

### Nunca Commitear:
```
❌ NO incluir .env en git
❌ NO guardar passwords en código
❌ NO commitar secrets
```

### Proteger .env:
```bash
# Permisos en Linux/Mac
chmod 600 .env

# PowerShell Windows
(Get-Item .env).Attributes = 'Hidden', 'System'
```

---

## 🚨 Detección de Amenazas

### Monitorear:

1. **Intentos de login fallidos**
```sql
-- Ver intentos de autenticación (agregar tabla)
SELECT * FROM login_attempts 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

2. **Cambios de rol**
```sql
SELECT * FROM users 
WHERE updated_at > NOW() - INTERVAL '1 day'
AND role != 'worker';
```

3. **Accesos inusuales**
```sql
SELECT assigned_by_user_id, COUNT(*) 
FROM session_assignments 
WHERE assigned_at > NOW() - INTERVAL '1 hour'
GROUP BY assigned_by_user_id;
```

4. **Usuarios nuevos**
```sql
SELECT username, email, role, created_at 
FROM users 
WHERE created_at > NOW() - INTERVAL '1 day';
```

---

## 🛡️ Configuración de Firewall

### Restricciones recomendadas:

```
✅ Permitir:
   - Tu IP a PostgreSQL (puerto 5432)
   - Rango de IPs de oficina a aplicación web
   - Acceso a HTTPS (443)

❌ Bloquear:
   - Acceso directo a BD desde internet
   - Puerto 5432 expuesto
   - HTTP sin HTTPS
   - Conexiones no autorizadas
```

---

## 🔄 Rotación de Credenciales

### Cada 90 días:

```bash
# 1. Cambiar contraseña admin
#    Mi Cuenta → Cambiar Contraseña

# 2. Cambiar DATABASE_URL si es necesario
#    Actualizar en .env

# 3. Revisar usuarios inactivos
#    Admin Panel → Desactivar usuarios no usados

# 4. Renovar certificados SSL
#    (Si usa HTTPS con certificados)
```

---

## 📝 Auditoría y Logs

### Información registrada:

✅ **Actualmente**
- Creación de usuarios (quién, cuándo)
- Asignación de sesiones (quién, a quién, cuándo)
- Cambios de rol

❌ **Falta agregar**
- Intentos de login fallidos
- Cambios de contraseña
- Desactivación de usuarios
- Acceso a admin panel
- Cambios de sesiones

### Implementar logs:

```python
# En auth_manager.py
import logging

logger = logging.getLogger(__name__)

def authenticate_user(self, username, password):
    try:
        user = auth.authenticate_user(username, password)
        if user:
            logger.info(f"Login exitoso: {username}")
        else:
            logger.warning(f"Intento fallido: {username}")
    except Exception as e:
        logger.error(f"Error de autenticación: {e}")
```

---

## 🆘 Recuperación de Desastres

### Si alguien accede sin autorización:

1. **Cambiar credenciales inmediatamente**
   ```bash
   # Cambiar contraseña postgresql
   ALTER USER usuario WITH PASSWORD 'nueva_contraseña_fuerte';
   ```

2. **Revisar accesos recientes**
   ```sql
   SELECT * FROM session_assignments 
   WHERE assigned_at > NOW() - INTERVAL '24 hours';
   ```

3. **Restaurar desde backup**
   ```bash
   # Restaurar base de datos
   psql -U postgres -d fonseca_canaca < backup.sql
   ```

4. **Desactivar usuarios sospechosos**
   ```sql
   UPDATE users 
   SET is_active = FALSE 
   WHERE username = 'usuario_sospechoso';
   ```

5. **Notificar a equipo**
   - Informar de incidente
   - Cambiar todas las contraseñas
   - Auditar logs

---

## 🎓 Capacitación de Usuarios

### Entrenar a usuarios en:

✅ **Contraseñas**
- Usar contraseñas fuertes (12+ caracteres)
- No compartir credenciales
- Cambiar regularmente

✅ **Datos sensibles**
- No poner información confidencial en notas
- Usar sesiones privadas

✅ **Phishing**
- No hacer click en links sospechosos
- Verificar URLs antes de ingresar

✅ **Reportar problemas**
- Contactar IT si hay actividad sospechosa
- No intentar "arreglarlo" solo

---

## 🔗 Referencias y Recursos

- [OWASP Top 10](https://owasp.org/Top10/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-syntax.html)
- [bcrypt Documentation](https://github.com/pyca/bcrypt)
- [Streamlit Security](https://docs.streamlit.io/library/advanced-features/server-configuration)

---

## Contacto de Seguridad

Para reportar vulnerabilidades:
📧 security@fonseca-canaca.local

**No abrir issues públicas para vulnerabilidades.**

---

**Última actualización:** Diciembre 2024
**Versión:** 1.0
