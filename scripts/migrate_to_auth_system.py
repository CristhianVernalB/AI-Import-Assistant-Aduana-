"""
Script de migración de datos desde el SessionManager antiguo al nuevo sistema con usuarios.
Ejecutar solo UNA VEZ antes de poner en producción.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def migrate_to_new_system():
    """
    Migra las sesiones existentes al nuevo sistema de usuarios.
    Crea un usuario 'admin' por defecto si no existe.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL no está configurada en .env")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔄 Iniciando migración de datos...")
        
        # 1. Verificar si existe usuario admin
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        admin = cur.fetchone()
        
        if not admin:
            print("📝 Creando usuario administrador por defecto...")
            import hashlib
            
            admin_id = str(uuid.uuid4())
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            cur.execute("""
                INSERT INTO users (id, username, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, (admin_id, "admin", "admin@fonseca-canaca.local", password_hash, "admin"))
            
            print(f"✅ Usuario 'admin' creado (contraseña: admin123)")
            admin_id = admin_id
        else:
            admin_id = admin['id']
        
        # 2. Verificar sesiones sin usuario_id y asignarlas al admin
        cur.execute("""
            SELECT id FROM work_sessions WHERE user_id IS NULL
        """)
        
        sessions_without_user = cur.fetchall()
        
        if sessions_without_user:
            print(f"📋 Encontradas {len(sessions_without_user)} sesiones sin usuario...")
            
            for session in sessions_without_user:
                cur.execute("""
                    UPDATE work_sessions
                    SET user_id = %s
                    WHERE id = %s
                """, (admin_id, session['id']))
            
            print(f"✅ {len(sessions_without_user)} sesiones asignadas al admin")
        else:
            print("✅ Todas las sesiones ya tienen usuario asignado")
        
        # 3. Mostrar estadísticas
        cur.execute("SELECT COUNT(*) as total FROM users")
        total_users = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM work_sessions")
        total_sessions = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM session_documents")
        total_docs = cur.fetchone()['total']
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n" + "="*50)
        print("📊 MIGRACIÓN COMPLETADA")
        print("="*50)
        print(f"✅ Usuarios en el sistema: {total_users}")
        print(f"✅ Sesiones de trabajo: {total_sessions}")
        print(f"✅ Documentos en sesiones: {total_docs}")
        print("\n🔐 Para iniciar sesión:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n⚠️  IMPORTANTE: Cambiar la contraseña del admin después del primer login")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("🔐 SCRIPT DE MIGRACIÓN A NUEVO SISTEMA DE AUTENTICACIÓN")
    print("=" * 50)
    input("Presiona ENTER para continuar (o Ctrl+C para cancelar)...")
    
    migrate_to_new_system()
