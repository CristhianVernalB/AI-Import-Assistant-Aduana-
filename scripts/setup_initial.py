#!/usr/bin/env python
"""
Script de configuración inicial del sistema de autenticación.
Ejecutar una sola vez después de clonar/descargar el proyecto.

USO:
    python setup_initial.py
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Imprime un header formateado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step, text):
    """Imprime un paso numerado."""
    print(f"[PASO {step}] {text}")


def create_env_file():
    """Crea archivo .env con configuración inicial."""
    print_step(1, "Configurando variables de entorno...")
    
    env_path = Path(".env")
    if env_path.exists():
        print("   ℹ️  Archivo .env ya existe")
        return
    
    print("   Necesito información de tu base de datos:")
    
    db_user = input("   • Usuario PostgreSQL (default: postgres): ").strip() or "postgres"
    db_password = input("   • Contraseña PostgreSQL: ").strip()
    db_host = input("   • Host (default: localhost): ").strip() or "localhost"
    db_port = input("   • Puerto (default: 5432): ").strip() or "5432"
    db_name = input("   • Nombre base de datos (default: fonseca_canaca): ").strip() or "fonseca_canaca"
    
    admin_pass = input("   • Contraseña de admin (default: admin123): ").strip() or "admin123"
    
    env_content = f"""# Configuración de la Base de Datos
DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}

# Contraseña para registro de administrador
ADMIN_PASSWORD={admin_pass}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("   ✅ Archivo .env creado correctamente")


def setup_database():
    """Intenta conectar a la BD y ejecutar el SQL."""
    print_step(2, "Configurando base de datos...")
    
    # Verificar si PostgreSQL está disponible
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True
        )
        print(f"   ℹ️  {result.stdout.strip()}")
    except FileNotFoundError:
        print("   ❌ PostgreSQL no está instalado o no está en PATH")
        print("   Necesitas instalar PostgreSQL para continuar")
        return False
    
    # Cargar .env
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    
    print("   Necesito ejecutar SQL en la base de datos.")
    print("   ¿Cómo prefieres hacerlo?\n")
    
    print("   OPCIÓN 1: Automático (requiere psql en PATH)")
    print("   OPCIÓN 2: Manual (copia y pega el SQL)")
    
    option = input("\n   Selecciona opción (1 o 2): ").strip()
    
    if option == "1":
        # Ejecutar SQL automáticamente
        sql_file = Path("setup_database.sql")
        if not sql_file.exists():
            print("   ❌ Archivo setup_database.sql no encontrado")
            return False
        
        try:
            subprocess.run(
                ["psql", db_url, "-f", str(sql_file)],
                check=True,
                capture_output=True
            )
            print("   ✅ Base de datos configurada correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error ejecutando SQL: {e}")
            return False
    
    else:
        # Mostrar SQL para copia manual
        print("\n   Ejecuta este SQL en tu cliente PostgreSQL:\n")
        
        sql_content = """
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
"""
        
        print(sql_content)
        
        input("\n   Presiona ENTER cuando hayas ejecutado el SQL en PostgreSQL...")
        print("   ✅ Continuando...\n")
        
        return True


def test_connection():
    """Prueba la conexión a la BD."""
    print_step(3, "Probando conexión a base de datos...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        import psycopg2
        db_url = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        print(f"   ✅ Conexión exitosa (usuarios en BD: {count})")
        return True
    
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False


def migrate_data():
    """Ofrece migrar datos existentes."""
    print_step(4, "Migrando datos existentes...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        import psycopg2
        db_url = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM work_sessions")
        session_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        if session_count > 0:
            print(f"   ℹ️  Encontradas {session_count} sesiones existentes")
            
            respuesta = input("   ¿Deseas ejecutar la migración automática? (s/n): ").lower()
            
            if respuesta == 's':
                try:
                    subprocess.run(
                        [sys.executable, "migrate_to_auth_system.py"],
                        check=True
                    )
                    print("   ✅ Migración completada")
                except subprocess.CalledProcessError:
                    print("   ❌ Error en la migración")
            else:
                print("   ℹ️  Puedes ejecutar la migración después con: python migrate_to_auth_system.py")
        else:
            print("   ℹ️  No hay sesiones anteriores que migrar")
    
    except Exception as e:
        print(f"   ℹ️  Migración no disponible: {e}")


def install_dependencies():
    """Instala las dependencias de Python."""
    print_step(5, "Verificando dependencias...")
    
    required_packages = ['psycopg2', 'python-dotenv', 'streamlit', 'pandas']
    
    try:
        for package in required_packages:
            __import__(package.replace('-', '_'))
        
        print("   ✅ Todas las dependencias están instaladas")
        return True
    
    except ImportError as missing:
        print(f"   ⚠️  Falta instalar: {missing}")
        
        respuesta = input("   ¿Instalar dependencias ahora? (s/n): ").lower()
        
        if respuesta == 's':
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    check=True
                )
                print("   ✅ Dependencias instaladas correctamente")
                return True
            except subprocess.CalledProcessError:
                print("   ❌ Error instalando dependencias")
                return False
        else:
            print("   ℹ️  Ejecuta: pip install -r requirements.txt")
            return False


def show_summary():
    """Muestra un resumen final."""
    print_header("CONFIGURACIÓN COMPLETADA ✅")
    
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│ 🎉 SISTEMA DE AUTENTICACIÓN CONFIGURADO CORRECTAMENTE              │
└─────────────────────────────────────────────────────────────────────┘

Para ejecutar la aplicación:
    streamlit run app_main.py

La aplicación se abrirá en: http://localhost:8501

Credenciales de prueba:
    Usuario: admin
    Contraseña: [la que configuraste en ADMIN_PASSWORD]

Documentación:
    • SETUP_GUIA_RAPIDA.md      → Guía de instalación
    • API_REFERENCE.md           → Referencia de funciones
    • SECURITY_GUIDE.md          → Seguridad y mejoras
    • EXAMPLES.py                → Ejemplos de código

Próximos pasos:
    1. Ejecuta: streamlit run app_main.py
    2. Inicia sesión con usuario: admin
    3. Crea nuevos usuarios en Panel Admin
    4. ¡Comienza a procesar documentos!

⚠️  IMPORTANTE ANTES DE PRODUCCIÓN:
    • Cambiar contraseña de admin
    • Configurar HTTPS
    • Realizar backups regulares
    • Revisar SECURITY_GUIDE.md

""")


def main():
    """Función principal."""
    print_header("CONFIGURACIÓN INICIAL - SISTEMA DE AUTENTICACIÓN")
    
    print("""
Este script configurará:
  ✓ Variables de entorno (.env)
  ✓ Base de datos PostgreSQL
  ✓ Usuarios iniciales
  ✓ Dependencias de Python

""")
    
    # Ejecutar pasos
    create_env_file()
    
    if not setup_database():
        print("   ⚠️  No se pudo configurar la BD. Puedes hacerlo manualmente después.")
    
    if not test_connection():
        print("   ⚠️  No se pudo conectar. Verifica tu .env")
        return
    
    migrate_data()
    
    if not install_dependencies():
        print("   ⚠️  Instala dependencias manualmente con: pip install -r requirements.txt")
        return
    
    show_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
