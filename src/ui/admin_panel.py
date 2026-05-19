"""
Módulo de panel de administración para gestionar usuarios y sesiones.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
"""
Módulo de panel de administración para gestionar usuarios y sesiones.
"""
import streamlit as st
from ..auth.auth_manager import AuthManager
from ..core.session_manager_extended import SessionManagerExtended
import pandas as pd
from datetime import datetime


def show_admin_panel():
    """Muestra el panel de administración."""
    st.header("⚙️ Panel de Administración")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["Gestión de Usuarios", "Gestión de Sesiones", "Reportes"])
    
    # === GESTIÓN DE USUARIOS ===
    with tab1:
        st.subheader("👥 Gestión de Usuarios")
        
        auth_manager = AuthManager()
        workers = auth_manager.get_all_workers()
        
        # Subtabs
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Crear Nuevo Usuario")
            
            with st.form("create_user_form"):
                new_username = st.text_input("Nombre de usuario")
                new_email = st.text_input("Email")
                new_password = st.text_input("Contraseña", type="password")
                new_role = st.selectbox("Rol", ["worker", "admin"])
                
                if st.form_submit_button("Crear Usuario", use_container_width=True, type="primary"):
                    if not all([new_username, new_email, new_password]):
                        st.error("Por favor completa todos los campos")
                    elif len(new_password) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres")
                    else:
                        result = auth_manager.create_user(new_username, new_email, new_password, new_role)
                        if "success" in result:
                            st.success(f"Usuario '{new_username}' creado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('error')}")
        
        with col2:
            st.write("### Usuarios Activos")
            
            if workers:
                for worker in workers:
                    with st.container(border=True):
                        col_name, col_actions = st.columns([3, 1])
                        
                        with col_name:
                            st.write(f"**{worker['username']}**")
                            st.caption(f"📧 {worker['email']}")
                            st.caption(f"Rol: {worker['role'].upper()}")
                        
                        with col_actions:
                            if st.button("⋮", key=f"user_menu_{worker['id']}", use_container_width=True):
                                st.session_state[f"show_user_options_{worker['id']}"] = not st.session_state.get(f"show_user_options_{worker['id']}", False)
                        
                        if st.session_state.get(f"show_user_options_{worker['id']}", False):
                            st.divider()
                            
                            # Opciones de usuario
                            col_opt1, col_opt2 = st.columns(2)
                            
                            with col_opt1:
                                if worker['role'] == 'worker':
                                    if st.button("Promocionar a Admin", key=f"promote_{worker['id']}", use_container_width=True):
                                        result = auth_manager.update_user_role(worker['id'], 'admin')
                                        if "success" in result:
                                            st.success("Usuario promocionado")
                                            st.rerun()
                                else:
                                    if st.button("Degradar a Worker", key=f"demote_{worker['id']}", use_container_width=True):
                                        result = auth_manager.update_user_role(worker['id'], 'worker')
                                        if "success" in result:
                                            st.success("Usuario degradado")
                                            st.rerun()
                            
                            with col_opt2:
                                if st.button("🗑️ Desactivar", key=f"deactivate_{worker['id']}", use_container_width=True):
                                    result = auth_manager.deactivate_user(worker['id'])
                                    if "success" in result:
                                        st.success("Usuario desactivado")
                                        st.rerun()
            else:
                st.info("No hay usuarios registrados")
    
    # === GESTIÓN DE SESIONES ===
    with tab2:
        st.subheader("📋 Gestión de Sesiones de Trabajo")
        
        session_manager = SessionManagerExtended()
        all_sessions = session_manager.get_all_sessions()
        
        if all_sessions:
            # Filtros
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                status_filter = st.multiselect(
                    "Filtrar por estado",
                    ["in_progress", "completed", "error", "paused"],
                    default=["in_progress"]
                )
            
            with col_filter2:
                worker_filter = st.selectbox(
                    "Filtrar por trabajador",
                    ["Todos"] + [w['username'] for w in workers],
                    key="worker_filter"
                )
            
            # Filtrar sesiones
            filtered_sessions = all_sessions
            
            if status_filter:
                filtered_sessions = [s for s in filtered_sessions if s['processing_status'] in status_filter]
            
            if worker_filter != "Todos":
                filtered_sessions = [s for s in filtered_sessions if s['assigned_to_name'] == worker_filter or s['created_by'] == worker_filter]
            
            # Mostrar sesiones
            for session in filtered_sessions:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**{session['session_name']}**")
                        st.caption(f"Creada por: {session['created_by']}")
                        
                        if session['assigned_to_name']:
                            st.caption(f"Asignada a: {session['assigned_to_name']}")
                        else:
                            st.caption("Asignada a: *Sin asignar*")
                        
                        st.caption(f"📅 {session['created_at'].strftime('%d/%m/%Y %H:%M')}")
                    
                    with col2:
                        status_color = {
                            'in_progress': '🔵',
                            'completed': '✅',
                            'error': '❌',
                            'paused': '⏸️'
                        }
                        st.write(f"{status_color.get(session['processing_status'], '❓')} {session['processing_status'].upper()}")
                        st.write(f"📄 {session['total_documents']} docs")
                        st.write(f"⚠️ {session['documents_with_errors']} errores")
                    
                    with col3:
                        if st.button("Ver Detalles", key=f"session_detail_{session['id']}", use_container_width=True):
                            st.session_state[f"show_session_{session['id']}"] = not st.session_state.get(f"show_session_{session['id']}", False)
                    
                    # Detalles expandidos
                    if st.session_state.get(f"show_session_{session['id']}", False):
                        st.divider()
                        
                        # Opciones de asignación
                        st.write("**Reasignar sesión:**")
                        new_worker = st.selectbox(
                            "Selecciona un trabajador",
                            [w['username'] for w in workers],
                            key=f"reassign_worker_{session['id']}"
                        )
                        
                        reassign_notes = st.text_area(
                            "Notas de la reasignación",
                            key=f"reassign_notes_{session['id']}"
                        )
                        
                        col_assign1, col_assign2 = st.columns(2)
                        
                        with col_assign1:
                            if st.button("Reasignar", key=f"do_reassign_{session['id']}", use_container_width=True, type="primary"):
                                worker_id = next(w['id'] for w in workers if w['username'] == new_worker)
                                result = session_manager.assign_session_to_worker(
                                    session['id'],
                                    worker_id,
                                    st.session_state.user_id,
                                    reassign_notes
                                )
                                
                                if "success" in result:
                                    st.success(f"Sesión reasignada a {new_worker}")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {result.get('error')}")
                        
                        with col_assign2:
                            if st.button("Eliminar Sesión", key=f"delete_session_{session['id']}", use_container_width=True, type="secondary"):
                                result = session_manager.delete_session(session['id'])
                                if "success" in result:
                                    st.success("Sesión eliminada")
                                    st.rerun()
                        
                        # Historial de asignaciones
                        history = session_manager.get_session_assignments_history(session['id'])
                        if history:
                            st.write("**Historial de asignaciones:**")
                            for assignment in history:
                                st.caption(f"📌 {assignment['assigned_at'].strftime('%d/%m/%Y %H:%M')} - Asignado a {assignment['assigned_to']} por {assignment['assigned_by']}")
                                if assignment['notes']:
                                    st.caption(f"Notas: {assignment['notes']}")
        else:
            st.info("No hay sesiones registradas")
    
    # === REPORTES ===
    with tab3:
        st.subheader("📊 Reportes")
        
        session_manager = SessionManagerExtended()
        
        # Carga de trabajo de cada trabajador
        st.write("### Carga de Trabajo por Trabajador")
        
        workload_data = []
        for worker in workers:
            workload = session_manager.get_worker_workload(worker['id'])
            workload_data.append({
                'Usuario': worker['username'],
                'Sesiones Totales': workload.get('total_sessions', 0),
                'En Progreso': workload.get('in_progress_sessions', 0),
                'Documentos': workload.get('total_documents', 0),
                'Con Errores': workload.get('documents_with_errors', 0)
            })
        
        if workload_data:
            df_workload = pd.DataFrame(workload_data)
            st.dataframe(df_workload, use_container_width=True)
            
            # Gráficos
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("### Sesiones por Trabajador")
                chart_data = df_workload[['Usuario', 'Sesiones Totales', 'En Progreso']].set_index('Usuario')
                st.bar_chart(chart_data)
            
            with col_chart2:
                st.write("### Documentos por Trabajador")
                chart_data = df_workload[['Usuario', 'Documentos', 'Con Errores']].set_index('Usuario')
                st.bar_chart(chart_data)
        else:
            st.info("No hay datos de carga de trabajo")


def show_worker_dashboard():
    """Muestra el dashboard de un trabajador."""
    st.header("📊 Mi Dashboard")
    
    session_manager = SessionManagerExtended()
    
    # Resumen de carga de trabajo
    workload = session_manager.get_worker_workload(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sesiones Totales", workload.get('total_sessions', 0))
    
    with col2:
        st.metric("En Progreso", workload.get('in_progress_sessions', 0))
    
    with col3:
        st.metric("Documentos", workload.get('total_documents', 0))
    
    with col4:
        st.metric("Con Errores", workload.get('documents_with_errors', 0))
    
    st.divider()
    
    # Mis sesiones
    st.subheader("📋 Mis Sesiones")
    
    my_sessions = session_manager.get_user_sessions(st.session_state.user_id)
    
    if my_sessions:
        for session in my_sessions:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{session['session_name']}**")
                    st.caption(f"Creada: {session['created_at'].strftime('%d/%m/%Y %H:%M')}")
                    st.caption(f"Estado: {session['processing_status'].upper()}")
                    st.caption(f"📄 {session['total_documents']} documentos | ⚠️ {session['documents_with_errors']} errores")
                
                with col2:
                    if st.button("Abrir", key=f"open_session_{session['id']}", use_container_width=True):
                        st.session_state.current_session = session['id']
    else:
        st.info("No tienes sesiones asignadas")
