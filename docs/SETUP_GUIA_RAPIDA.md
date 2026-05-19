# 🔐 SISTEMA DE AUTENTICACIÓN - GUÍA RÁPIDA DE INSTALACIÓN

## 📋 Requisitos Previos

- PostgreSQL 12+ instalado
- Python 3.8+ instalado
- Acceso a la terminal/línea de comandos

## 🚀 Instalación Paso a Paso

### PASO 1: Preparar la Base de Datos

#### 1.1 Conectarse a PostgreSQL

```powershell
psql -U postgres
```

#### 1.2 Ejecutar el SQL de configuración

Copia y ejecuta TODO este SQL en PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'worker',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS work_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    user_notes TEXT,
    total_documents INTEGER DEFAULT 0,
    documents_with_errors INTEGER DEFAULT 0,
    processing_status VARCHAR(50) DEFAULT 'in_progress',
    session_data JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS session_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES work_sessions(id) ON DELETE CASCADE,
    document_index INTEGER NOT NULL,
    filename VARCHAR(500),
    original_data JSONB NOT NULL,
    edited_data JSONB,
    validation_status VARCHAR(50) DEFAULT 'pending',
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES work_sessions(id) ON DELETE CASCADE,
    assigned_from_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON work_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON work_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_assigned_to ON work_sessions(assigned_to);
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_assignments_session_id ON session_assignments(session_id);
```

✅ Verificar que las tablas se crearon correctamente:

```sql
\dt
```

### PASO 2: Configurar Variables de Entorno

#### 2.1 Crear archivo `.env`

En la carpeta raíz del proyecto (junto a `app.py`), crear un archivo llamado `.env` con:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_base_datos
ADMIN_PASSWORD=admin123
```

**Reemplaza:**
- `usuario` - tu usuario de PostgreSQL (ej: postgres)
- `contraseña` - tu contraseña de PostgreSQL
- `localhost` - tu servidor (localhost si está local)
- `5432` - puerto (5432 por defecto)
- `nombre_base_datos` - nombre de tu base de datos

**EJEMPLO REAL:**
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/fonseca_canaca
ADMIN_PASSWORD=miContraseñaSegura2024
```

### PASO 3: Instalar Dependencias Python

```powershell
pip install -r requirements.txt
```

Las librerías principales ya están incluidas:
- `psycopg2` ✅ (conexión a PostgreSQL)
- `python-dotenv` ✅ (variables de entorno)
- `streamlit` ✅ (interfaz web)

### PASO 4: Ejecutar la Migración (PRIMERA VEZ SOLO)

Si tienes datos previos en la base de datos, ejecuta:

```powershell
python migrate_to_auth_system.py
```

Este script:
- Crea usuario 'admin' automáticamente
- Asigna sesiones antiguas al admin
- Muestra estadísticas

**Credenciales por defecto:**
```
Usuario: admin
Contraseña: admin123
```

### PASO 5: Ejecutar la Aplicación

```powershell
streamlit run app_main.py
```

La aplicación se abrirá en: `http://localhost:8501`

## 🎯 Primeros Pasos en la Aplicación

### 1️⃣ Pantalla de Login

Verás dos opciones:

**OPCIÓN A: Iniciar Sesión (usuarios existentes)**
- Usuario: `admin`
- Contraseña: `admin123`

**OPCIÓN B: Crear Nuevo Usuario (solo admin)**
- Contraseña de admin: `admin123` (cambiar en `.env`)
- Crear nuevo usuario con rol 'worker' o 'admin'

### 2️⃣ Panel de Administración (solo para admins)

Una vez logueado como admin, tendrás acceso a:

**👥 Gestión de Usuarios**
- ➕ Crear nuevos usuarios
- 📝 Cambiar rol (admin ↔ worker)
- 🗑️ Desactivar usuarios

**📋 Gestión de Sesiones**
- 📊 Ver todas las sesiones
- 🔄 Reasignar sesiones entre trabajadores
- 📜 Ver historial de cambios
- ⚠️ Seguimiento de errores

**📈 Reportes**
- 👥 Carga de trabajo por persona
- 📊 Gráficos de actividad
- 📋 Estadísticas generales

### 3️⃣ Dashboard de Trabajador

Los trabajadores ven:
- ✅ Sus sesiones asignadas
- 📊 Estadísticas personales
- 📝 Procesar documentos
- 🔐 Cambiar contraseña

## 🔄 Flujo de Trabajo Recomendado

```
1. ADMIN crea usuario WORKER
        ↓
2. WORKER inicia sesión
        ↓
3. WORKER crea sesión de trabajo
        ↓
4. WORKER procesa documentos
        ↓
5. WORKER finaliza sesión
        ↓
6. ADMIN revisa sesión completada
        ↓
7. ADMIN reasigna otra sesión a WORKER
```

## 🐛 Solución de Problemas

### Error: "DATABASE_URL no está configurada"
✅ Crear archivo `.env` con `DATABASE_URL=...`

### Error: "Error conectando a la base de datos"
✅ Verificar credenciales en `.env`
✅ Verificar que PostgreSQL está corriendo
✅ Verificar puerto (5432 por defecto)

### Error: "Usuario o contraseña incorrectos"
✅ Ejecutar `migrate_to_auth_system.py` para crear usuario admin
✅ Usar usuario `admin` con contraseña `admin123`

### Olvidé contraseña de admin
⚠️ Necesitarás acceso directo a la base de datos:
```sql
UPDATE users 
SET password_hash = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
WHERE username = 'admin';
-- Esta es la contraseña hasheada de "admin123"
```

## 📁 Archivos Importantes

| Archivo | Descripción |
|---------|------------|
| `app_main.py` | 🚀 Aplicación principal (ejecutar esto) |
| `auth_manager.py` | 🔐 Gestor de autenticación |
| `session_manager_extended.py` | 📋 Gestor de sesiones |
| `login_interface.py` | 🎨 Interfaz de login |
| `admin_panel.py` | ⚙️ Panel de administración |
| `migrate_to_auth_system.py` | 🔄 Migración de datos |
| `.env` | 🔑 Configuración (crear manualmente) |

## 🔐 Seguridad

### Antes de Producción ⚠️

```powershell
# 1. Cambiar contraseña del admin en la aplicación
#    Mi Cuenta → Cambiar Contraseña

# 2. Crear usuarios para cada trabajador
#    Panel Admin → Gestión de Usuarios → Crear Usuario

# 3. Cambiar ADMIN_PASSWORD en .env
#    Usar una contraseña fuerte y segura

# 4. Hacer backup de la base de datos
psql -U postgres -d fonseca_canaca -f backup.sql

# 5. Configurar backups automáticos
#    (depende de tu sistema operativo/servidor)
```

## 📞 Soporte

Para problemas, contacta al equipo de desarrollo con:
- ❌ Mensaje de error exacto
- 📄 Archivo de logs (si aplica)
- 🖥️ Sistema operativo
- 🔧 Versión de PostgreSQL

---

**¡Listo! Tu sistema de autenticación está configurado. 🎉**
