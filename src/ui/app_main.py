"""
Aplicación principal con integración de login y panel de administración.
Este archivo reemplaza el app.py anterior y proporciona la estructura completa.
"""
"""
Aplicación principal con integración de login y panel de administración.
Este archivo reemplaza el app.py anterior y proporciona la estructura completa.
"""
import streamlit as st
from ..auth.login_interface import show_login_page, check_authentication, show_user_menu, get_current_user
from .admin_panel import show_admin_panel, show_worker_dashboard
import traceback

# --- Configuración Inicial de la Página ---
st.set_page_config(layout="wide", page_title="Asistente de Importaciones IA - Sistema Completo")

# Inicializar estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# === LÓGICA PRINCIPAL ===
if not check_authentication():
    # Mostrar página de login si no está autenticado
    show_login_page()
else:
    # Usuario autenticado - mostrar aplicación principal
    st.set_page_config(layout="wide", page_title=f"Asistente IA - {st.session_state.username}")
    
    # Sidebar con información del usuario
    with st.sidebar:
        st.image("https://via.placeholder.com/200x50?text=Logo", use_column_width=True)
        st.divider()
        show_user_menu()
        st.divider()
        
        # Menú de navegación según el rol
        st.write("### 📑 Menú")
        
        if st.session_state.user_role == 'admin':
            page = st.radio(
                "Selecciona una página",
                ["Dashboard", "Panel de Administración", "Mi Cuenta"]
            )
        else:
            page = st.radio(
                "Selecciona una página",
                ["Dashboard", "Mi Cuenta"]
            )
    
    """
    Aplicación principal con integración de login y panel de administración.
    Este archivo reemplaza el app.py anterior y proporciona la estructura completa.
    """
    import streamlit as st
    from ..auth.login_interface import show_login_page, check_authentication, show_user_menu, get_current_user
    from .admin_panel import show_admin_panel, show_worker_dashboard
    import traceback

    # --- Configuración Inicial de la Página ---
    st.set_page_config(layout="wide", page_title="Asistente de Importaciones IA - Sistema Completo")

    # Inicializar estado de sesión
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

    # === LÓGICA PRINCIPAL ===
    if not check_authentication():
        # Mostrar página de login si no está autenticado
        show_login_page()
    else:
        # Usuario autenticado - mostrar aplicación principal
        st.set_page_config(layout="wide", page_title=f"Asistente IA - {st.session_state.username}")
    
        # Sidebar con información del usuario
        with st.sidebar:
            st.image("https://via.placeholder.com/200x50?text=Logo", use_column_width=True)
            st.divider()
            show_user_menu()
            st.divider()
        
            # Menú de navegación según el rol
            st.write("### 📑 Menú")
        
            if st.session_state.user_role == 'admin':
                page = st.radio(
                    "Selecciona una página",
                    ["Dashboard", "Panel de Administración", "Mi Cuenta"]
                )
            else:
                page = st.radio(
                    "Selecciona una página",
                    ["Dashboard", "Mi Cuenta"]
                )
    
        try:
            # Renderizar página seleccionada
            if page == "Dashboard":
                if st.session_state.user_role == 'admin':
                    show_admin_panel()
                else:
                    show_worker_dashboard()
        
            elif page == "Panel de Administración":
                if st.session_state.user_role == 'admin':
                    show_admin_panel()
                else:
                    st.error("❌ No tienes permisos para acceder a esta sección")
        
            elif page == "Mi Cuenta":
                st.header("👤 Mi Cuenta")
            
                user = get_current_user()
            
                col1, col2 = st.columns(2)
            
                with col1:
                    st.write("### Información de Cuenta")
                    st.write(f"**Usuario:** {user['username']}")
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Rol:** {user['role'].upper()}")
            
                with col2:
                    st.write("### Cambiar Contraseña")
                
                    from ..auth.auth_manager import AuthManager
                
                    with st.form("change_password_form"):
                        old_password = st.text_input("Contraseña Actual", type="password")
                        new_password = st.text_input("Nueva Contraseña", type="password")
                        new_password_confirm = st.text_input("Confirmar Nueva Contraseña", type="password")
                    
                        if st.form_submit_button("Cambiar Contraseña", use_container_width=True, type="primary"):
                            if not all([old_password, new_password, new_password_confirm]):
                                st.error("Por favor completa todos los campos")
                            elif new_password != new_password_confirm:
                                st.error("Las nuevas contraseñas no coinciden")
                            elif len(new_password) < 6:
                                st.error("La contraseña debe tener al menos 6 caracteres")
                            else:
                                auth_manager = AuthManager()
                                result = auth_manager.change_password(user['id'], old_password, new_password)
                            
                                if "success" in result:
                                    st.success("✅ Contraseña actualizada correctamente")
                                else:
                                    st.error(f"❌ {result.get('error')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.error(traceback.format_exc())
