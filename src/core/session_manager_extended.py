"""
Extensión del gestor de sesiones para soportar múltiples usuarios y asignaciones.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import uuid
import json
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class SessionManagerExtended:
    """Gestor extendido de sesiones de trabajo con soporte para usuarios y asignaciones."""
    
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
    
    def create_work_session(self, user_id: str, session_name: str, session_data: Dict[str, Any], 
                           user_notes: str = "") -> Dict[str, Any]:
        """
        Crea una nueva sesión de trabajo para un usuario.
        
        Args:
            user_id: ID del usuario creador
            session_name: Nombre de la sesión
            session_data: Datos JSON de la sesión
            user_notes: Notas del usuario (opcional)
        
        Returns:
            Diccionario con datos de la sesión creada
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            session_id = str(uuid.uuid4())
            
            cur.execute("""
                INSERT INTO work_sessions 
                (id, user_id, session_name, session_data, user_notes, processing_status)
                VALUES (%s, %s, %s, %s, %s, 'in_progress')
                RETURNING id, user_id, session_name, created_at, processing_status
            """, (session_id, user_id, session_name, json.dumps(session_data), user_notes))
            
            session = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "session": dict(session)}
        
        except Exception as e:
            return {"error": f"Error creando sesión: {str(e)}"}
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene todas las sesiones de un usuario (creadas o asignadas)."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Sesiones creadas por el usuario O asignadas al usuario
            cur.execute("""
                SELECT 
                    ws.id,
                    ws.user_id,
                    ws.session_name,
                    ws.created_at,
                    ws.updated_at,
                    ws.assigned_to,
                    ws.user_notes,
                    ws.total_documents,
                    ws.documents_with_errors,
                    ws.processing_status,
                    u.username as created_by,
                    a.username as assigned_to_name
                FROM work_sessions ws
                LEFT JOIN users u ON ws.user_id = u.id
                LEFT JOIN users a ON ws.assigned_to = a.id
                WHERE ws.user_id = %s OR ws.assigned_to = %s
                ORDER BY ws.created_at DESC
            """, (user_id, user_id))
            
            sessions = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return sessions
        
        except Exception as e:
            print(f"Error obteniendo sesiones del usuario: {e}")
            return []
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Obtiene todas las sesiones (admin only)."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT 
                    ws.id,
                    ws.user_id,
                    ws.session_name,
                    ws.created_at,
                    ws.updated_at,
                    ws.assigned_to,
                    ws.user_notes,
                    ws.total_documents,
                    ws.documents_with_errors,
                    ws.processing_status,
                    u.username as created_by,
                    a.username as assigned_to_name
                FROM work_sessions ws
                LEFT JOIN users u ON ws.user_id = u.id
                LEFT JOIN users a ON ws.assigned_to = a.id
                ORDER BY ws.created_at DESC
            """)
            
            sessions = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return sessions
        
        except Exception as e:
            print(f"Error obteniendo todas las sesiones: {e}")
            return []
    
    def assign_session_to_worker(self, session_id: str, worker_id: str, 
                                 assigned_by_user_id: str, notes: str = "") -> Dict[str, Any]:
        """
        Asigna una sesión a un trabajador diferente.
        
        Args:
            session_id: ID de la sesión
            worker_id: ID del trabajador a asignar
            assigned_by_user_id: ID del admin/usuario que realiza la asignación
            notes: Notas sobre la asignación
        
        Returns:
            Diccionario con resultado de la operación
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Actualizar sesión
            cur.execute("""
                UPDATE work_sessions
                SET assigned_to = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, session_name, assigned_to
            """, (worker_id, session_id))
            
            session = cur.fetchone()
            
            if not session:
                return {"error": "Sesión no encontrada"}
            
            # Registrar en historial de asignaciones
            assignment_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO session_assignments 
                (id, session_id, assigned_from_user_id, assigned_to_user_id, notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (assignment_id, session_id, assigned_by_user_id, worker_id, notes))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "session": dict(session)}
        
        except Exception as e:
            return {"error": f"Error asignando sesión: {str(e)}"}
    
    def get_session_assignments_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de asignaciones de una sesión."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT 
                    sa.id,
                    sa.assigned_at,
                    u1.username as assigned_by,
                    u2.username as assigned_to,
                    sa.notes
                FROM session_assignments sa
                LEFT JOIN users u1 ON sa.assigned_from_user_id = u1.id
                LEFT JOIN users u2 ON sa.assigned_to_user_id = u2.id
                WHERE sa.session_id = %s
                ORDER BY sa.assigned_at DESC
            """, (session_id,))
            
            history = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return history
        
        except Exception as e:
            print(f"Error obteniendo historial de asignaciones: {e}")
            return []
    
    def get_worker_workload(self, worker_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo de un trabajador."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Total de sesiones asignadas
            cur.execute("""
                SELECT COUNT(*) as total_sessions
                FROM work_sessions
                WHERE assigned_to = %s
            """, (worker_id,))
            
            total = cur.fetchone()['total_sessions']
            
            # Sesiones en progreso
            cur.execute("""
                SELECT COUNT(*) as in_progress_sessions
                FROM work_sessions
                WHERE assigned_to = %s AND processing_status = 'in_progress'
            """, (worker_id,))
            
            in_progress = cur.fetchone()['in_progress_sessions']
            
            # Total de documentos
            cur.execute("""
                SELECT SUM(total_documents) as total_docs
                FROM work_sessions
                WHERE assigned_to = %s
            """, (worker_id,))
            
            total_docs = cur.fetchone()['total_docs'] or 0
            
            # Documentos con errores
            cur.execute("""
                SELECT SUM(documents_with_errors) as error_docs
                FROM work_sessions
                WHERE assigned_to = %s
            """, (worker_id,))
            
            error_docs = cur.fetchone()['error_docs'] or 0
            
            cur.close()
            conn.close()
            
            return {
                "total_sessions": total,
                "in_progress_sessions": in_progress,
                "total_documents": total_docs,
                "documents_with_errors": error_docs
            }
        
        except Exception as e:
            print(f"Error obteniendo carga de trabajo: {e}")
            return {}
    
    def update_session_status(self, session_id: str, new_status: str) -> Dict[str, Any]:
        """Actualiza el estado de procesamiento de una sesión."""
        valid_statuses = ['in_progress', 'completed', 'error', 'paused']
        
        if new_status not in valid_statuses:
            return {"error": f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"}
        
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                UPDATE work_sessions
                SET processing_status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, session_name, processing_status
            """, (new_status, session_id))
            
            session = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "session": dict(session)} if session else {"error": "Sesión no encontrada"}
        
        except Exception as e:
            return {"error": f"Error actualizando sesión: {str(e)}"}
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Elimina una sesión y sus documentos asociados."""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # El DELETE CASCADE de la tabla work_sessions eliminará los documentos automáticamente
            cur.execute("""
                DELETE FROM work_sessions
                WHERE id = %s
                RETURNING id, session_name
            """, (session_id,))
            
            session = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return {"success": True, "deleted": dict(session)} if session else {"error": "Sesión no encontrada"}
        
        except Exception as e:
            return {"error": f"Error eliminando sesión: {str(e)}"}
