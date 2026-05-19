-- ============================================================================
-- SCRIPT DE CONFIGURACIÓN DE BASE DE DATOS
-- Sistema de Autenticación - Fonseca Canaca
-- ============================================================================
-- 
-- USO:
--   psql -U usuario -d nombre_base_datos -f setup_database.sql
--
-- O manualmente:
--   psql -U postgres
--   \c tu_base_datos
--   [Pega este contenido]
-- ============================================================================

-- Crear extensión UUID si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLA: users (Autenticación y gestión de usuarios)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'worker' CHECK (role IN ('admin', 'worker')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'Tabla de usuarios del sistema';
COMMENT ON COLUMN users.username IS 'Nombre de usuario único';
COMMENT ON COLUMN users.password_hash IS 'Hash SHA256 de la contraseña';
COMMENT ON COLUMN users.role IS 'Rol: admin (administrador) o worker (trabajador)';
COMMENT ON COLUMN users.is_active IS 'True si el usuario está activo, False si está desactivado';

-- ============================================================================
-- TABLA: work_sessions (Sesiones de trabajo - MODIFICADA)
-- ============================================================================
-- Esta tabla se crea con una estructura nueva que incluye soporte para usuarios
-- Si ya tienes esta tabla, necesitarás migrar los datos primero
-- Ver: migrate_to_auth_system.py

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
    processing_status VARCHAR(50) DEFAULT 'in_progress' 
        CHECK (processing_status IN ('in_progress', 'completed', 'error', 'paused')),
    session_data JSONB NOT NULL
);

COMMENT ON TABLE work_sessions IS 'Sesiones de trabajo de procesamiento de documentos';
COMMENT ON COLUMN work_sessions.user_id IS 'Usuario que creó la sesión (clave foránea)';
COMMENT ON COLUMN work_sessions.assigned_to IS 'Usuario actual asignado para procesar (puede cambiar)';
COMMENT ON COLUMN work_sessions.processing_status IS 'Estado actual: in_progress, completed, error, paused';
COMMENT ON COLUMN work_sessions.session_data IS 'Datos de la sesión en formato JSON';

-- ============================================================================
-- TABLA: session_documents (Documentos en sesiones)
-- ============================================================================
CREATE TABLE IF NOT EXISTS session_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES work_sessions(id) ON DELETE CASCADE,
    document_index INTEGER NOT NULL,
    filename VARCHAR(500),
    original_data JSONB NOT NULL,
    edited_data JSONB,
    validation_status VARCHAR(50) DEFAULT 'pending' 
        CHECK (validation_status IN ('pending', 'validated', 'error', 'corrected')),
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE session_documents IS 'Documentos individuales dentro de una sesión';
COMMENT ON COLUMN session_documents.session_id IS 'Sesión a la que pertenece este documento (clave foránea)';
COMMENT ON COLUMN session_documents.original_data IS 'Datos originales extraídos del documento';
COMMENT ON COLUMN session_documents.edited_data IS 'Datos editados/corregidos por el usuario';

-- ============================================================================
-- TABLA: session_assignments (Historial de asignaciones - AUDITORÍA)
-- ============================================================================
CREATE TABLE IF NOT EXISTS session_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES work_sessions(id) ON DELETE CASCADE,
    assigned_from_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

COMMENT ON TABLE session_assignments IS 'Historial de reasignaciones de sesiones (auditoría)';
COMMENT ON COLUMN session_assignments.assigned_from_user_id IS 'Usuario que realizó la reasignación (generalmente admin)';
COMMENT ON COLUMN session_assignments.assigned_to_user_id IS 'Usuario al que se reasignó';
COMMENT ON COLUMN session_assignments.notes IS 'Notas sobre la reasignación';

-- ============================================================================
-- ÍNDICES - Para optimizar búsquedas y rendimiento
-- ============================================================================

-- Índices en tabla users
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Índices en tabla work_sessions
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON work_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON work_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_assigned_to ON work_sessions(assigned_to);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON work_sessions(processing_status);

-- Índices en tabla session_documents
CREATE INDEX IF NOT EXISTS idx_session_documents_session_id ON session_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_session_documents_validation_status ON session_documents(validation_status);

-- Índices en tabla session_assignments
CREATE INDEX IF NOT EXISTS idx_assignments_session_id ON session_assignments(session_id);
CREATE INDEX IF NOT EXISTS idx_assignments_assigned_to ON session_assignments(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_assigned_at ON session_assignments(assigned_at DESC);

-- ============================================================================
-- DATOS INICIALES (Opcional)
-- ============================================================================
-- Este comentario evita que se inserte datos por accidente
-- Descomenta la sección siguiente si deseas crear un usuario admin inicial
--
-- INSERT INTO users (id, username, email, password_hash, role, is_active)
-- VALUES (
--     uuid_generate_v4(),
--     'admin',
--     'admin@fonseca-canaca.local',
--     '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', -- hash de 'admin123'
--     'admin',
--     TRUE
-- );

-- ============================================================================
-- VERIFICACIÓN - Mostrar tabla creadas
-- ============================================================================
-- Descomenta para ver las tablas creadas (solo en desarrollo)
--
-- \dt
-- \di

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
-- Si todo se ejecutó correctamente, deberías ver:
-- ✅ Extension "uuid-ossp" creada
-- ✅ Tabla "users" creada
-- ✅ Tabla "work_sessions" creada
-- ✅ Tabla "session_documents" creada
-- ✅ Tabla "session_assignments" creada
-- ✅ Índices creados
-- ============================================================================
