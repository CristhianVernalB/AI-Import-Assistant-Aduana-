# 📚 Referencia de API - Sistema de Autenticación

## AuthManager

Clase para gestionar autenticación y usuarios.

### Inicialización
```python
from auth_manager import AuthManager

auth = AuthManager()
```

### Métodos

#### `create_user(username, email, password, role='worker')`
**Descripción:** Crea un nuevo usuario en la base de datos.

**Parámetros:**
- `username` (str): Nombre único del usuario
- `email` (str): Email único
- `password` (str): Contraseña en texto plano (será hasheada)
- `role` (str): 'admin' o 'worker' (default: 'worker')

**Retorna:**
```python
# Éxito
{"success": True, "user": {"id": "...", "username": "...", "email": "...", "role": "..."}}

# Error
{"error": "El usuario o email ya existe"}
```

**Ejemplo:**
```python
result = auth.create_user("juan", "juan@mail.com", "pass123", "worker")
if "success" in result:
    print(f"Usuario creado: {result['user']['username']}")
```

---

#### `authenticate_user(username, password)`
**Descripción:** Autentica un usuario y retorna sus datos.

**Parámetros:**
- `username` (str): Nombre del usuario
- `password` (str): Contraseña en texto plano

**Retorna:**
```python
# Éxito
{"id": "...", "username": "...", "email": "...", "role": "...", "created_at": "..."}

# Error (retorna None)
None
```

**Ejemplo:**
```python
user = auth.authenticate_user("juan", "pass123")
if user:
    print(f"Bienvenido {user['username']}")
else:
    print("Credenciales inválidas")
```

---

#### `get_user(user_id)`
**Descripción:** Obtiene los datos de un usuario por su ID.

**Parámetros:**
- `user_id` (str): UUID del usuario

**Retorna:**
```python
{"id": "...", "username": "...", "email": "...", "role": "...", "is_active": True, ...}
```

**Ejemplo:**
```python
user = auth.get_user("550e8400-e29b-41d4-a716-446655440000")
```

---

#### `get_all_workers()`
**Descripción:** Obtiene lista de todos los trabajadores activos.

**Retorna:**
```python
[
    {"id": "...", "username": "juan", "email": "juan@mail.com", "role": "worker", ...},
    {"id": "...", "username": "maria", "email": "maria@mail.com", "role": "worker", ...}
]
```

**Ejemplo:**
```python
workers = auth.get_all_workers()
for worker in workers:
    print(f"- {worker['username']}")
```

---

#### `update_user_role(user_id, new_role)`
**Descripción:** Actualiza el rol de un usuario.

**Parámetros:**
- `user_id` (str): UUID del usuario
- `new_role` (str): 'admin' o 'worker'

**Retorna:**
```python
{"success": True, "user": {...}}
```

**Ejemplo:**
```python
result = auth.update_user_role("550e8400-e29b-41d4-a716-446655440000", "admin")
```

---

#### `change_password(user_id, old_password, new_password)`
**Descripción:** Cambia la contraseña de un usuario.

**Parámetros:**
- `user_id` (str): UUID del usuario
- `old_password` (str): Contraseña actual
- `new_password` (str): Nueva contraseña

**Retorna:**
```python
{"success": True, "message": "Contraseña actualizada correctamente"}
{"error": "Contraseña actual incorrecta"}
```

---

#### `deactivate_user(user_id)`
**Descripción:** Desactiva un usuario (soft delete).

**Parámetros:**
- `user_id` (str): UUID del usuario

**Retorna:**
```python
{"success": True, "deleted": {"id": "...", "username": "..."}}
```

---

#### `hash_password(password)`
**Descripción:** Hashea una contraseña (interno).

---

#### `verify_password(password, password_hash)`
**Descripción:** Verifica si una contraseña coincide con su hash (interno).

---

## SessionManagerExtended

Clase para gestionar sesiones de trabajo con soporte multi-usuario.

### Inicialización
```python
from session_manager_extended import SessionManagerExtended

session_mgr = SessionManagerExtended()
```

### Métodos

#### `create_work_session(user_id, session_name, session_data, user_notes='')`
**Descripción:** Crea una nueva sesión de trabajo.

**Parámetros:**
- `user_id` (str): UUID del usuario creador
- `session_name` (str): Nombre descriptivo de la sesión
- `session_data` (dict): Datos en formato diccionario (se convierte a JSON)
- `user_notes` (str): Notas opcionales (default: '')

**Retorna:**
```python
{"success": True, "session": {"id": "...", "session_name": "...", "created_at": "..."}}
```

**Ejemplo:**
```python
result = session_mgr.create_work_session(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    session_name="Importación Enero 2024",
    session_data={"month": "2024-01", "total_files": 25},
    user_notes="Documentos de proveedores internacionales"
)
session_id = result['session']['id']
```

---

#### `get_user_sessions(user_id)`
**Descripción:** Obtiene todas las sesiones de un usuario (creadas o asignadas).

**Parámetros:**
- `user_id` (str): UUID del usuario

**Retorna:**
```python
[
    {
        "id": "...",
        "session_name": "Importación Enero 2024",
        "created_by": "juan",
        "assigned_to_name": "maria",
        "processing_status": "in_progress",
        "total_documents": 25,
        "documents_with_errors": 3,
        ...
    }
]
```

---

#### `get_all_sessions()`
**Descripción:** Obtiene todas las sesiones del sistema (admin only).

**Retorna:**
```python
[...]  # Lista completa de todas las sesiones
```

---

#### `assign_session_to_worker(session_id, worker_id, assigned_by_user_id, notes='')`
**Descripción:** Reasigna una sesión a un trabajador diferente.

**Parámetros:**
- `session_id` (str): UUID de la sesión
- `worker_id` (str): UUID del nuevo trabajador
- `assigned_by_user_id` (str): UUID del admin que realiza la reasignación
- `notes` (str): Notas sobre la reasignación (default: '')

**Retorna:**
```python
{"success": True, "session": {...}}
```

**Ejemplo:**
```python
result = session_mgr.assign_session_to_worker(
    session_id="550e8400-e29b-41d4-a716-446655440000",
    worker_id="660e8400-e29b-41d4-a716-446655440001",
    assigned_by_user_id="admin-uuid",
    notes="Reasignado por balanceo de carga"
)
```

---

#### `get_session_assignments_history(session_id)`
**Descripción:** Obtiene el historial de asignaciones de una sesión.

**Parámetros:**
- `session_id` (str): UUID de la sesión

**Retorna:**
```python
[
    {
        "assigned_at": "2024-01-15 10:30:00",
        "assigned_by": "admin",
        "assigned_to": "maria",
        "notes": "Reasignado por disponibilidad"
    }
]
```

---

#### `get_worker_workload(worker_id)`
**Descripción:** Obtiene estadísticas de carga de trabajo de un trabajador.

**Parámetros:**
- `worker_id` (str): UUID del trabajador

**Retorna:**
```python
{
    "total_sessions": 5,
    "in_progress_sessions": 2,
    "total_documents": 150,
    "documents_with_errors": 12
}
```

**Ejemplo:**
```python
workload = session_mgr.get_worker_workload("worker-uuid")
print(f"Documentos por procesar: {workload['total_documents']}")
```

---

#### `update_session_status(session_id, new_status)`
**Descripción:** Actualiza el estado de una sesión.

**Parámetros:**
- `session_id` (str): UUID de la sesión
- `new_status` (str): 'in_progress', 'completed', 'error', o 'paused'

**Retorna:**
```python
{"success": True, "session": {...}}
```

**Ejemplo:**
```python
result = session_mgr.update_session_status(session_id, "completed")
```

---

#### `delete_session(session_id)`
**Descripción:** Elimina una sesión y todos sus documentos asociados.

**Parámetros:**
- `session_id` (str): UUID de la sesión

**Retorna:**
```python
{"success": True, "deleted": {"id": "...", "session_name": "..."}}
```

---

## LoginInterface (Streamlit)

Funciones auxiliares para la interfaz de Streamlit.

### `show_login_page()`
Muestra la página de login con opciones de iniciar sesión y registro.

### `check_authentication()`
Verifica si el usuario está autenticado. Retorna bool.

### `logout()`
Cierra la sesión del usuario actual.

### `get_current_user()`
Retorna los datos del usuario autenticado actualmente.

```python
user = get_current_user()
# {"id": "...", "username": "...", "role": "...", "email": "..."}
```

### `show_user_menu()`
Muestra un menú con información del usuario en el sidebar.

---

## AdminPanel (Streamlit)

### `show_admin_panel()`
Muestra el panel completo de administración con:
- Gestión de usuarios
- Gestión de sesiones
- Reportes y gráficos

### `show_worker_dashboard()`
Muestra el dashboard personal del trabajador.

---

## Códigos de Error Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| DATABASE_URL not set | Variable de entorno faltante | Crear archivo `.env` |
| User already exists | Usuario o email duplicado | Usar otro nombre/email |
| Authentication failed | Credenciales incorrectas | Verificar usuario/password |
| Session not found | ID de sesión inválido | Verificar UUID |
| Permission denied | Rol insuficiente | Solo admins pueden hacer esto |

---

## Integración con Sesiones Antigua

El código anterior (`session_manager.py`) sigue siendo compatible. Puedes:

1. Mantener ambos módulos
2. Migrar gradualmente usando `migrate_to_auth_system.py`
3. Usar SessionManagerExtended que hereda las funcionalidades básicas

---

## Mejores Prácticas

✅ **Haz esto:**
- Validar input del usuario
- Usar try/except para errores de base de datos
- Verificar roles antes de acciones críticas
- Registrar cambios importantes

❌ **No hagas esto:**
- Guardar contraseñas en texto plano
- Confiar en cliente para validaciones
- Olvidar hacer backups
- Usar credenciales por defecto en producción
