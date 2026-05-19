# Sistema de Autenticación y Gestión de Sesiones

## 📋 Descripción

Este documento describe la integración del sistema de login y gestión de usuarios para la aplicación "Asistente de Importaciones IA".

## 🗄️ Base de Datos

### SQL a ejecutar en PostgreSQL

Ejecuta el siguiente SQL en tu base de datos PostgreSQL:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'worker', -- 'admin' o 'worker'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de sesiones de trabajo (modificada para incluir usuario)
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

-- Tabla de documentos en sesiones
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

-- Tabla de historial de asignaciones (para auditoría)
CREATE TABLE IF NOT EXISTS session_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES work_sessions(id) ON DELETE CASCADE,
    assigned_from_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON work_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON work_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_assigned_to ON work_sessions(assigned_to);
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_assignments_session_id ON session_assignments(session_id);
```

## 🔧 Configuración

### 1. Archivo .env

Crea un archivo `.env` en la raíz del proyecto con tus credenciales:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_db
ADMIN_PASSWORD=tu_contraseña_segura_aqui
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Cómo ejecutar

### Opción 1: Usar el nuevo app principal (RECOMENDADO)

```bash
streamlit run app_main.py
```

### Opción 2: Mantener el app.py anterior

El `app.py` original sigue funcionando para procesamiento de documentos. Los nuevos módulos se pueden integrar gradualmente.

## 👤 Funcionalidades de Login

### Pantalla de Inicio
- **Login**: Autenticación de usuarios existentes
- **Registro (Admin)**: Solo administradores pueden crear nuevas cuentas
  - Requiere contraseña de administrador
  - Define roles (worker/admin) al crear usuarios

### Panel de Administrador (Admin)

#### Gestión de Usuarios
- ✅ Ver todos los trabajadores activos
- ✅ Crear nuevos usuarios
- ✅ Promocionar trabajadores a administradores
- ✅ Degradar administradores a trabajadores
- ✅ Desactivar usuarios

#### Gestión de Sesiones
- ✅ Ver todas las sesiones de trabajo
- ✅ Filtrar por estado (en progreso, completada, error, pausada)
- ✅ Filtrar por trabajador
- ✅ Reasignar sesiones entre trabajadores
- ✅ Ver historial de asignaciones
- ✅ Eliminar sesiones
- ✅ Notas de reasignación para auditoría

#### Reportes
- 📊 Carga de trabajo por trabajador
- 📊 Gráficos de sesiones y documentos
- 📊 Estadísticas de errores

### Dashboard de Trabajador

- 📋 Ver sesiones creadas o asignadas
- 📊 Estadísticas personales
- 👤 Ver y cambiar contraseña

## 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|------------|
| `auth_manager.py` | Gestor de autenticación y usuarios |
| `session_manager_extended.py` | Extensión del gestor de sesiones con soporte multi-usuario |
| `login_interface.py` | Interfaz de login para Streamlit |
| `admin_panel.py` | Panel de administración para gestionar usuarios y sesiones |
| `app_main.py` | Aplicación principal integrada con autenticación |
| `.env.example` | Plantilla de configuración de variables de entorno |

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con SHA256
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Historial de auditoría para asignaciones
- ✅ Variables de entorno para configuración sensible
- ⚠️ **IMPORTANTE**: Cambiar `ADMIN_PASSWORD` en producción

## 🔄 Flujo de Trabajo Completo

1. **Creación de usuario**: Admin crea cuenta de trabajador
2. **Login**: Trabajador inicia sesión
3. **Creación de sesión**: Trabajador crea una sesión de trabajo
4. **Procesamiento**: Trabajador procesa documentos en la sesión
5. **Reasignación**: Admin puede reasignar sesión a otro trabajador
6. **Auditoría**: Historial de cambios disponible para revisión

## 📞 Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.
