"""
Gestor de autenticación y usuarios para la aplicación.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import uuid
import hashlib
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class AuthManager:
    """Gestor de autenticación y usuarios en PostgreSQL."""
    
    def __init__(self):
        """Inicializa la conexión con la base de datos."""
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL no está configurada en .env")
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos."""
        try:
            return psycopg2.connect(self.db_url)
        except psycopg2.OperationalError as e:
            raise ValueError(f"Error conectando a la base de datos: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hashea una contraseña usando SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica si una contraseña coincide con su hash."""
        return self.hash_password(password) == password_hash
    
    def create_user(self, username: str, email: str, password: str, role: str = "worker") -> Dict[str, Any]:
        """
        Crea un nuevo usuario.
        
        Args:
            username: Nombre de usuario único
            email: Email único
            password: Contraseña en texto plano (será hasheada)
            role: 'admin' o 'worker'
        
        Returns:
            Diccionario con datos del usuario creado o error
        """
        if role not in ["admin", "worker"]:
            return {"error": "El rol debe ser 'admin' o 'worker'"}
        
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Verificar que el usuario y email no existan
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cur.fetchone():
                return {"error": "El usuario o email ya existe"}
            
            # Crear usuario
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            cur.execute("""
                INSERT INTO users (id, username, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                RETURNING id, username, email, role, created_at
            """, (user_id, username, email, password_hash, role))
            
            user = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "user": dict(user)}
        
        except Exception as e:
            return {"error": f"Error creando usuario: {str(e)}"}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
        
        Returns:
            Diccionario con datos del usuario si es válido, None si no
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, username, email, role, is_active, created_at
                FROM users
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if not user:
                return None
            
            # Obtener hash sin la query anterior (necesario para comparación)
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT password_hash FROM users WHERE id = %s", (user['id'],))
            password_data = cur.fetchone()
            cur.close()
            conn.close()
            
            if not password_data or not self.verify_password(password, password_data['password_hash']):
                return None
            
            return dict(user)
        
        except Exception as e:
            print(f"Error autenticando usuario: {e}")
            return None
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de un usuario por su ID."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, username, email, role, is_active, created_at, updated_at
                FROM users
                WHERE id = %s
            """, (user_id,))
            
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            return dict(user) if user else None
        
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    def get_all_workers(self) -> List[Dict[str, Any]]:
        """Obtiene lista de todos los trabajadores (workers)."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, username, email, role, is_active, created_at
                FROM users
                WHERE role = 'worker' AND is_active = TRUE
                ORDER BY username
            """)
            
            workers = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return workers
        
        except Exception as e:
            print(f"Error obteniendo trabajadores: {e}")
            return []
    
    def update_user_role(self, user_id: str, new_role: str) -> Dict[str, Any]:
        """Actualiza el rol de un usuario (admin only)."""
        if new_role not in ["admin", "worker"]:
            return {"error": "El rol debe ser 'admin' o 'worker'"}
        
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                UPDATE users
                SET role = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, username, email, role
            """, (new_role, user_id))
            
            user = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "user": dict(user)} if user else {"error": "Usuario no encontrado"}
        
        except Exception as e:
            return {"error": f"Error actualizando usuario: {str(e)}"}
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Verificar contraseña antigua
            cur.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            
            if not user_data or not self.verify_password(old_password, user_data['password_hash']):
                return {"error": "Contraseña actual incorrecta"}
            
            # Actualizar contraseña
            new_password_hash = self.hash_password(new_password)
            cur.execute("""
                UPDATE users
                SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_password_hash, user_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "message": "Contraseña actualizada correctamente"}
        
        except Exception as e:
            return {"error": f"Error cambiando contraseña: {str(e)}"}
    
    def deactivate_user(self, user_id: str) -> Dict[str, Any]:
        """Desactiva un usuario (admin only)."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                UPDATE users
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, username
            """, (user_id,))
            
            user = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "user": dict(user)} if user else {"error": "Usuario no encontrado"}
        
        except Exception as e:
            return {"error": f"Error desactivando usuario: {str(e)}"}
