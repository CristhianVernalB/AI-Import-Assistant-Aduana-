"""
EJEMPLOS DE USO - Sistema de Autenticación y Gestión de Sesiones

Este archivo muestra ejemplos de cómo usar los nuevos módulos de autenticación.
"""

# ============================================================================
# EJEMPLO 1: Autenticación de Usuarios (auth_manager.py)
# ============================================================================

from auth_manager import AuthManager

auth = AuthManager()

# 1.1 - Crear un nuevo usuario
result = auth.create_user(
    username="juan_perez",
    email="juan@example.com",
    password="contraseña123",
    role="worker"
)
print(result)
# Output: {"success": True, "user": {...}}

# 1.2 - Autenticar usuario
user = auth.authenticate_user("juan_perez", "contraseña123")
if user:
    print(f"Usuario autenticado: {user['username']} ({user['role']})")
else:
    print("Credenciales incorrectas")

# 1.3 - Obtener información del usuario
user_data = auth.get_user("user-id-uuid")
print(user_data)

# 1.4 - Obtener todos los trabajadores
workers = auth.get_all_workers()
for worker in workers:
    print(f"- {worker['username']} ({worker['role']})")

# 1.5 - Cambiar rol de usuario (admin -> worker o vice versa)
result = auth.update_user_role("user-id-uuid", "admin")

# 1.6 - Cambiar contraseña
result = auth.change_password(
    user_id="user-id-uuid",
    old_password="contraseña123",
    new_password="nueva_contraseña"
)

# 1.7 - Desactivar usuario
result = auth.deactivate_user("user-id-uuid")


# ============================================================================
# EJEMPLO 2: Gestión de Sesiones Extendida (session_manager_extended.py)
# ============================================================================

from session_manager_extended import SessionManagerExtended

session_mgr = SessionManagerExtended()

# 2.1 - Crear una nueva sesión de trabajo
result = session_mgr.create_work_session(
    user_id="admin-user-id",
    session_name="Importación Mercancías Enero 2024",
    session_data={
        "total_files": 15,
        "source": "email",
        "date_range": "2024-01-01 to 2024-01-31"
    },
    user_notes="Documentación de facturación internacional"
)
print(result)
# Output: {"success": True, "session": {...}}

# 2.2 - Obtener sesiones del usuario (creadas o asignadas)
user_sessions = session_mgr.get_user_sessions("user-id-uuid")
for session in user_sessions:
    print(f"- {session['session_name']} ({session['processing_status']})")

# 2.3 - Obtener todas las sesiones (admin only)
all_sessions = session_mgr.get_all_sessions()

# 2.4 - Reasignar sesión a otro trabajador
result = session_mgr.assign_session_to_worker(
    session_id="session-uuid",
    worker_id="new-worker-uuid",
    assigned_by_user_id="admin-uuid",
    notes="Reasignado por alto volumen en sesión anterior"
)

# 2.5 - Ver historial de asignaciones de una sesión
history = session_mgr.get_session_assignments_history("session-uuid")
for assignment in history:
    print(f"Asignado a {assignment['assigned_to']} por {assignment['assigned_by']}")

# 2.6 - Ver carga de trabajo de un trabajador
workload = session_mgr.get_worker_workload("worker-uuid")
print(f"Sesiones: {workload['total_sessions']}")
print(f"En progreso: {workload['in_progress_sessions']}")
print(f"Documentos: {workload['total_documents']}")
print(f"Con errores: {workload['documents_with_errors']}")

# 2.7 - Actualizar estado de sesión
result = session_mgr.update_session_status("session-uuid", "completed")

# 2.8 - Eliminar sesión
result = session_mgr.delete_session("session-uuid")


# ============================================================================
# EJEMPLO 3: Usando en Streamlit (app_main.py)
# ============================================================================

# El archivo app_main.py ya incluye toda la lógica de Streamlit
# Simplemente ejecuta:
# $ streamlit run app_main.py

# La autenticación se verifica automáticamente y se redirige al login si es necesario.


# ============================================================================
# EJEMPLO 4: Migrando datos del sistema anterior
# ============================================================================

# Para migrar sesiones existentes sin usuarios:
# $ python migrate_to_auth_system.py

# Este script:
# 1. Crea un usuario 'admin' por defecto
# 2. Asigna todas las sesiones sin usuario al admin
# 3. Muestra estadísticas de migración


# ============================================================================
# EJEMPLO 5: Control de Acceso Basado en Roles (RBAC)
# ============================================================================

def admin_only_action():
    """Ejemplo de función que solo admins pueden usar"""
    if st.session_state.user_role != 'admin':
        st.error("Solo administradores pueden acceder a esta sección")
        return
    
    # Código exclusivo para admins
    show_admin_panel()

def worker_dashboard():
    """Ejemplo de dashboard para trabajadores"""
    session_mgr = SessionManagerExtended()
    
    workload = session_mgr.get_worker_workload(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sesiones", workload['total_sessions'])
    with col2:
        st.metric("En Progreso", workload['in_progress_sessions'])
    with col3:
        st.metric("Documentos", workload['total_documents'])
    with col4:
        st.metric("Errores", workload['documents_with_errors'])


# ============================================================================
# EJEMPLO 6: Flujo Completo de Trabajo
# ============================================================================

"""
ESCENARIO: Importación de facturas de proveedores

PASOS:
1. Admin crea usuario 'maria' (trabajador)
2. Maria inicia sesión
3. Maria crea una sesión "Facturas Enero 2024"
4. Maria procesa documentos en la sesión
5. Maria termina, sesión pasa a 'completed'
6. Admin ve todas las sesiones y carga de trabajo
7. Admin reasigna otra sesión a Maria

CÓDIGO:
"""

from auth_manager import AuthManager
from session_manager_extended import SessionManagerExtended
import uuid

# Paso 1: Admin crea usuario Maria
auth = AuthManager()
result = auth.create_user("maria", "maria@empresa.com", "segura123", "worker")
maria_id = result['user']['id']

# Paso 2: Maria se autentica
maria = auth.authenticate_user("maria", "segura123")
assert maria is not None

# Paso 3: Maria crea una sesión
session_mgr = SessionManagerExtended()
result = session_mgr.create_work_session(
    user_id=maria_id,
    session_name="Facturas Enero 2024",
    session_data={"month": "2024-01"},
    user_notes="Facturas de proveedores internacionales"
)
session_id = result['session']['id']

# Paso 4: Maria procesa documentos (esto sucede en la aplicación)

# Paso 5: Maria termina (la sesión se marca como completada)
session_mgr.update_session_status(session_id, "completed")

# Paso 6: Admin ve todas las sesiones
all_sessions = session_mgr.get_all_sessions()
for session in all_sessions:
    print(f"{session['session_name']} - {session['processing_status']}")

# Paso 7: Admin reasigna otra sesión
# (Primero crear otra sesión)
result2 = session_mgr.create_work_session(
    user_id=maria_id,
    session_name="Facturas Febrero 2024",
    session_data={"month": "2024-02"}
)
session_id_2 = result2['session']['id']

# Reasignar a otro trabajador
result = session_mgr.assign_session_to_worker(
    session_id=session_id_2,
    worker_id="another-worker-uuid",
    assigned_by_user_id="admin-uuid",
    notes="Reasignado para balancear carga"
)


# ============================================================================
# NOTAS DE SEGURIDAD
# ============================================================================

"""
✅ IMPLEMENTADO:
- Hasheo de contraseñas SHA256
- Control de roles (admin/worker)
- Histórico de auditoría para asignaciones
- Desactivación de usuarios (soft delete)
- Variables de entorno para credenciales

⚠️ TODO EN PRODUCCIÓN:
- Cambiar ADMIN_PASSWORD por una contraseña fuerte
- Usar HTTPS en la aplicación
- Implementar 2FA (autenticación de dos factores)
- Usar bcrypt o argon2 en lugar de SHA256 para contraseñas
- Implementar rate limiting en login
- Hacer backup regular de la base de datos
- Revisar logs de auditoría regularmente
- Usar SSL para conexión a PostgreSQL
"""
