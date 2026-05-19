"""
Módulo de interfaz de login para Streamlit.
Maneja la pantalla de autenticación y registro de usuarios.
"""
import streamlit as st
from .auth_manager import AuthManager
from datetime import datetime

def show_login_page():
    """Muestra la página de login."""
    st.set_page_config(layout="wide", page_title="Login - Sistema de Importaciones")
    
    # Centro la página con columnas
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://via.placeholder.com/300x100?text=Logo+Empresa", use_column_width=True)
        st.title("🔐 Asistente de Importaciones IA")
        st.subheader("Sistema de Gestión de Documentos")
        
        # Tabs para Login y Registro
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registro (Admin)"])
        
        # === TAB DE LOGIN ===
        with tab1:
            st.write("Ingresa tus credenciales para acceder al sistema")
            
            username = st.text_input("👤 Usuario", key="login_username")
            password = st.text_input("🔑 Contraseña", type="password", key="login_password")
            
            if st.button("Iniciar Sesión", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Por favor completa todos los campos")
                else:
                    auth_manager = AuthManager()
                    user = auth_manager.authenticate_user(username, password)
                    
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user_role = user['role']
                        st.session_state.user_email = user['email']
                        st.success(f"¡Bienvenido {user['username']}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
        
        # === TAB DE REGISTRO ===
        with tab2:
            st.write("**Solo administradores pueden crear nuevas cuentas de usuario**")
            
            admin_password = st.text_input("🔐 Contraseña de Administrador", type="password", key="admin_password")
            
            if admin_password:  # Solo mostrar campos si ingresa contraseña admin
                if admin_password == "admin123":  # CAMBIAR ESTO EN PRODUCCIÓN
                    st.success("✅ Acceso de administrador confirmado")
                    
                    new_username = st.text_input("👤 Nuevo Usuario", key="new_username")
                    new_email = st.text_input("📧 Email", key="new_email")
                    new_password = st.text_input("🔑 Contraseña", type="password", key="new_password")
                    new_password_confirm = st.text_input("🔑 Confirmar Contraseña", type="password", key="new_password_confirm")
                    
                    user_role = st.selectbox("👨‍💼 Rol del Usuario", ["worker", "admin"])
                    
                    if st.button("Crear Usuario", use_container_width=True, type="primary"):
                        if not all([new_username, new_email, new_password, new_password_confirm]):
                            st.error("Por favor completa todos los campos")
                        elif new_password != new_password_confirm:
                            st.error("Las contraseñas no coinciden")
                        elif len(new_password) < 6:
                            st.error("La contraseña debe tener al menos 6 caracteres")
                        else:
                            auth_manager = AuthManager()
                            result = auth_manager.create_user(new_username, new_email, new_password, user_role)
                            
                            if "success" in result:
                                st.success(f"✅ Usuario '{new_username}' creado exitosamente")
                                st.info(f"Rol: {user_role}")
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                else:
                    st.error("❌ Contraseña de administrador incorrecta")
        
        st.divider()
        st.caption("🔒 Sistema seguro. Tus datos están protegidos.")


def check_authentication():
    """Verifica si el usuario está autenticado."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    return st.session_state.authenticated


def logout():
    """Cierra la sesión del usuario actual."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_role = None
    st.session_state.user_email = None
    st.success("Sesión cerrada correctamente")
    st.rerun()


def get_current_user():
    """Obtiene los datos del usuario autenticado actualmente."""
    if st.session_state.authenticated:
        return {
            'id': st.session_state.user_id,
            'username': st.session_state.username,
            'role': st.session_state.user_role,
            'email': st.session_state.user_email
        }
    return None


def show_user_menu():
    """Muestra un menú con información del usuario autenticado."""
    if st.session_state.authenticated:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"👤 **{st.session_state.username}**")
            st.caption(f"Rol: {st.session_state.user_role.upper()}")
        
        with col3:
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                logout()
