import streamlit as st
from cruds import usuarios, instituciones, participantes, fases_completadas, demos
import datetime

def get_dashboard_data(conn, user):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total FROM instituciones")
    instituciones_count = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM participantes")
    participantes_count = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM fases_institucion WHERE estado = 'completado'")
    fases_completadas_count = cur.fetchone()["total"]

    return {
        "instituciones": instituciones_count,
        "participantes": participantes_count,
        "fases_completadas": fases_completadas_count
    }

def crud_usuarios(conn):
    st.subheader("Usuarios")
    action = st.selectbox("Acción", ["Listar", "Crear", "Actualizar", "Eliminar"], key="usuarios_action")
    if action == "Listar":
        data = usuarios.list_usuarios(conn)
        st.dataframe([dict(row) for row in data])
    elif action == "Crear":
        with st.form("crear_usuario"):
            nombre = st.text_input("Nombre")
            email = st.text_input("Email")
            password = st.text_input("Contraseña")
            rol = st.selectbox("Rol", ["admin", "comercial", "soporte"])
            submitted = st.form_submit_button("Crear")
            if submitted:
                from auth_utils import safe_password_hash
                hashed = safe_password_hash(password)
                try:
                    usuarios.create_usuario(conn, nombre, email, hashed, rol)
                    st.success("Usuario creado")
                except Exception as e:
                    st.error(f"Error: {e}")
    elif action == "Actualizar":
        # Seleccionar usuario por nombre
        data = usuarios.list_usuarios(conn)
        user_dict = {f"{row['nombre']} ({row['email']}, ID {row['id']})": row['id'] for row in data}
        user_names = list(user_dict.keys())
        if user_names:
            selected_user = st.selectbox("Selecciona usuario", user_names, key="upd_user_select")
            user_id = user_dict[selected_user]
            nombre = st.text_input("Nuevo nombre", key="upd_nombre")
            email = st.text_input("Nuevo email", key="upd_email")
            password = st.text_input("Nueva contraseña", key="upd_password")
            rol = st.selectbox("Nuevo rol", ["", "admin", "comercial", "soporte"], key="upd_rol")
            if st.button("Actualizar usuario"):
                fields = {}
                if nombre: fields["nombre"] = nombre
                if email: fields["email"] = email
                if password:
                    from auth_utils import safe_password_hash
                    fields["password"] = safe_password_hash(password)
                if rol: fields["rol"] = rol
                if fields:
                    usuarios.update_usuario(conn, user_id, **fields)
                    st.success("Usuario actualizado")
        else:
            st.info("No hay usuarios para actualizar.")
    elif action == "Eliminar":
        # Seleccionar usuario por nombre
        data = usuarios.list_usuarios(conn)
        user_dict = {f"{row['nombre']} ({row['email']}, ID {row['id']})": row['id'] for row in data}
        user_names = list(user_dict.keys())
        if user_names:
            selected_user = st.selectbox("Selecciona usuario", user_names, key="del_user_select")
            user_id = user_dict[selected_user]
            if st.button("Eliminar usuario"):
                usuarios.delete_usuario(conn, user_id)
                st.success("Usuario eliminado")
        else:
            st.info("No hay usuarios para eliminar.")

def crud_instituciones(conn):
    st.subheader("Instituciones")
    action = st.selectbox("Acción", ["Listar", "Crear", "Actualizar", "Eliminar"], key="instituciones_action")
    if action == "Listar":
        data = instituciones.list_instituciones(conn)
        st.dataframe([dict(row) for row in data])
    elif action == "Crear":
        with st.form("crear_institucion"):
            nombre = st.text_input("Nombre institución")
            responsable = st.text_input("Responsable")
            email_responsable = st.text_input("Email responsable")
            telefono_responsable = st.text_input("Teléfono responsable")
            submitted = st.form_submit_button("Crear")
            if submitted:
                instituciones.create_institucion(conn, nombre, responsable, email_responsable, telefono_responsable)
                st.success("Institución creada")
    elif action == "Actualizar":
        # Seleccionar institución por nombre
        data = instituciones.list_instituciones(conn)
        inst_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in data}
        inst_names = list(inst_dict.keys())
        if inst_names:
            selected_inst = st.selectbox("Selecciona institución", inst_names, key="upd_inst_select")
            inst_id = inst_dict[selected_inst]
            nombre = st.text_input("Nuevo nombre", key="upd_inst_nombre")
            responsable = st.text_input("Nuevo responsable", key="upd_inst_resp")
            email_responsable = st.text_input("Nuevo email responsable", key="upd_inst_email")
            telefono_responsable = st.text_input("Nuevo teléfono responsable", key="upd_inst_tel")
            estado = st.text_input("Nuevo estado", key="upd_inst_estado")
            if st.button("Actualizar institución"):
                fields = {}
                if nombre: fields["nombre"] = nombre
                if responsable: fields["responsable"] = responsable
                if email_responsable: fields["email_responsable"] = email_responsable
                if telefono_responsable: fields["telefono_responsable"] = telefono_responsable
                if estado: fields["estado"] = estado
                if fields:
                    instituciones.update_institucion(conn, inst_id, **fields)
                    st.success("Institución actualizada")
        else:
            st.info("No hay instituciones para actualizar.")
    elif action == "Eliminar":
        # Seleccionar institución por nombre
        data = instituciones.list_instituciones(conn)
        inst_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in data}
        inst_names = list(inst_dict.keys())
        if inst_names:
            selected_inst = st.selectbox("Selecciona institución", inst_names, key="del_inst_select")
            inst_id = inst_dict[selected_inst]
            if st.button("Eliminar institución"):
                instituciones.delete_institucion(conn, inst_id)
                st.success("Institución eliminada")
        else:
            st.info("No hay instituciones para eliminar.")

def crud_participantes(conn):
    st.subheader("Participantes")
    action = st.selectbox("Acción", ["Listar", "Crear", "Actualizar", "Eliminar"], key="participantes_action")
    if action == "Listar":
        data = participantes.list_participantes(conn)
        # Obtener todos los nombres de instituciones en un dict {id: nombre}
        insts = instituciones.list_instituciones(conn)
        inst_map = {row["id"]: row["nombre"] for row in insts}
        # Reemplazar institucion_id por nombre en los datos
        data_dicts = []
        for row in data:
            row_dict = dict(row)
            row_dict["institucion"] = inst_map.get(row_dict["institucion_id"], "Desconocida")
            del row_dict["institucion_id"]
            data_dicts.append(row_dict)
        st.dataframe(data_dicts)
    elif action == "Crear":
        # Obtener instituciones para el selector
        insts = instituciones.list_instituciones(conn)
        inst_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in insts}
        inst_names = list(inst_dict.keys())
        with st.form("crear_participante"):
            institucion_name = st.selectbox("Institución", inst_names)
            institucion_id = inst_dict[institucion_name] if inst_names else None
            nombre = st.text_input("Nombre participante")
            rol = st.selectbox("Rol", ["docente", "directivo"])
            email = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            submitted = st.form_submit_button("Crear")
            if submitted and institucion_id:
                participantes.create_participante(conn, institucion_id, nombre, rol, email, telefono)
                st.success("Participante creado")
    elif action == "Actualizar":
        # Seleccionar participante por nombre
        data = participantes.list_participantes(conn)
        part_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in data}
        part_names = list(part_dict.keys())
        if part_names:
            selected_part = st.selectbox("Selecciona participante", part_names, key="upd_part_select")
            part_id = part_dict[selected_part]
            nombre = st.text_input("Nuevo nombre", key="upd_part_nombre")
            rol = st.selectbox("Nuevo rol", ["", "docente", "directivo"], key="upd_part_rol")
            email = st.text_input("Nuevo email", key="upd_part_email")
            telefono = st.text_input("Nuevo teléfono", key="upd_part_tel")
            if st.button("Actualizar participante"):
                fields = {}
                if nombre: fields["nombre"] = nombre
                if rol: fields["rol"] = rol
                if email: fields["email"] = email
                if telefono: fields["telefono"] = telefono
                if fields:
                    participantes.update_participante(conn, part_id, **fields)
                    st.success("Participante actualizado")
        else:
            st.info("No hay participantes para actualizar.")
    elif action == "Eliminar":
        # Seleccionar participante por nombre
        data = participantes.list_participantes(conn)
        part_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in data}
        part_names = list(part_dict.keys())
        if part_names:
            selected_part = st.selectbox("Selecciona participante", part_names, key="del_part_select")
            part_id = part_dict[selected_part]
            if st.button("Eliminar participante"):
                participantes.delete_participante(conn, part_id)
                st.success("Participante eliminado")
        else:
            st.info("No hay participantes para eliminar.")

def crud_fases_completadas(conn):
    st.subheader("Fases Completadas por Institución")
    action = st.selectbox("Acción", ["Listar", "Crear", "Actualizar", "Eliminar"], key="fases_action")
    if action == "Listar":
        data = fases_completadas.list_fases_institucion(conn)
        st.dataframe([dict(row) for row in data])
    elif action == "Crear":
        # Selector de institución por nombre
        insts = instituciones.list_instituciones(conn)
        inst_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in insts}
        inst_names = list(inst_dict.keys())
        # Selector de responsable por nombre de usuario
        users = usuarios.list_usuarios(conn)
        user_dict = {f"{row['nombre']} ({row['email']}, ID {row['id']})": row['nombre'] for row in users}
        user_names = list(user_dict.keys())
        with st.form("crear_fase_inst"):
            institucion_name = st.selectbox("Institución", inst_names)
            institucion_id = inst_dict[institucion_name] if inst_names else None
            fase_id = st.number_input("ID Fase", min_value=1, step=1)
            estado = st.selectbox("Estado", ["pendiente", "en_progreso", "completado"])
            responsable_name = st.selectbox("Responsable", user_names)
            responsable = user_dict[responsable_name] if user_names else None
            submitted = st.form_submit_button("Crear")
            if submitted and institucion_id and responsable:
                fases_completadas.create_fase_institucion(conn, institucion_id, fase_id, estado, responsable)
                st.success("Fase-Institución creada")
    elif action == "Actualizar":
        fase_inst_id = st.number_input("ID de fase-institución a actualizar", min_value=1, step=1)
        estado = st.selectbox("Nuevo estado", ["", "pendiente", "en_progreso", "completado"], key="upd_fase_estado")
        responsable = st.text_input("Nuevo responsable", key="upd_fase_resp")
        if st.button("Actualizar fase-institución"):
            fields = {}
            if estado: fields["estado"] = estado
            if responsable: fields["responsable"] = responsable
            if fields:
                fases_completadas.update_fase_institucion(conn, fase_inst_id, **fields)
                st.success("Fase-Institución actualizada")
    elif action == "Eliminar":
        fase_inst_id = st.number_input("ID de fase-institución a eliminar", min_value=1, step=1, key="del_fase_inst")
        if st.button("Eliminar fase-institución"):
            fases_completadas.delete_fase_institucion(conn, fase_inst_id)
            st.success("Fase-Institución eliminada")

def gestión_demos_kanban(conn):
    """Panel Kanban para gestión de demos"""
    st.subheader("🎯 Gestión de Demos - Panel Kanban")
    
    # Estadísticas generales
    stats = demos.get_demos_estadisticas(conn)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📝 Total", stats["total"])
    with col2:
        st.metric("⏳ Pendientes", stats["pendiente"])
    with col3:
        st.metric("🔄 En Progreso", stats["en_progreso"])
    with col4:
        st.metric("✅ Completadas", stats["completado"])
    with col5:
        st.metric("❌ Canceladas", stats["cancelado"])
    
    st.divider()
    
    # Formulario para crear nueva demo
    with st.expander("➕ Crear Nueva Demo"):
        with st.form("nueva_demo"):
            col1, col2 = st.columns(2)
            with col1:
                titulo = st.text_input("Título de la Demo*")
                descripcion = st.text_area("Descripción")
                prioridad = st.selectbox("Prioridad", ["baja", "media", "alta"])
            
            with col2:
                # Selector de institución
                insts = instituciones.list_instituciones(conn)
                inst_options = ["Sin asignar"] + [f"{inst['nombre']} (ID: {inst['id']})" for inst in insts]
                inst_selected = st.selectbox("Institución", inst_options)
                
                # Selector de responsable
                users = usuarios.list_usuarios(conn)
                user_options = ["Sin asignar"] + [f"{user['nombre']} ({user['email']})" for user in users]
                resp_selected = st.selectbox("Responsable", user_options)
                
                fecha_limite = st.date_input("Fecha límite (opcional)", value=None)
            
            submitted = st.form_submit_button("Crear Demo", type="primary")
            
            if submitted and titulo:
                # Procesar institución
                institucion_id = None
                if inst_selected != "Sin asignar":
                    for inst in insts:
                        if f"{inst['nombre']} (ID: {inst['id']})" == inst_selected:
                            institucion_id = inst['id']
                            break
                
                # Procesar responsable
                responsable = None
                if resp_selected != "Sin asignar":
                    for user in users:
                        if f"{user['nombre']} ({user['email']})" == resp_selected:
                            responsable = user['nombre']
                            break
                
                demos.create_demo(conn, titulo, descripcion, "pendiente", institucion_id, responsable, prioridad)
                st.success("Demo creada exitosamente!")
                st.rerun()
    
    st.divider()
    
    # Panel Kanban
    st.markdown("### 📋 Tablero Kanban")
    
    # Crear columnas para el kanban
    col_pendiente, col_progreso, col_completado, col_cancelado = st.columns(4)
    
    # Configuración de colores y estilos para cada columna
    estados = {
        "pendiente": {"color": "#FFA500", "icon": "⏳", "title": "Pendientes"},
        "en_progreso": {"color": "#007BFF", "icon": "🔄", "title": "En Progreso"},
        "completado": {"color": "#28A745", "icon": "✅", "title": "Completadas"},
        "cancelado": {"color": "#DC3545", "icon": "❌", "title": "Canceladas"}
    }
    
    columnas = [col_pendiente, col_progreso, col_completado, col_cancelado]
    estados_keys = list(estados.keys())
    
    for i, (estado, col) in enumerate(zip(estados_keys, columnas)):
        with col:
            config = estados[estado]
            st.markdown(f"""
                <div style="
                    background-color: {config['color']}20; 
                    border-left: 4px solid {config['color']}; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin-bottom: 10px;
                ">
                    <h4 style="margin: 0; color: {config['color']};">
                        {config['icon']} {config['title']}
                    </h4>
                </div>
            """, unsafe_allow_html=True)
            
            # Obtener demos de este estado
            demos_estado = demos.list_demos_by_estado(conn, estado)
            
            if not demos_estado:
                st.info("No hay demos en este estado")
            else:
                for demo in demos_estado:
                    # Crear tarjeta para cada demo
                    prioridad_color = {"alta": "#DC3545", "media": "#FFC107", "baja": "#6C757D"}
                    prioridad_icon = {"alta": "🔴", "media": "🟡", "baja": "🟢"}
                    
                    with st.container():
                        st.markdown(f"""
                            <div style="
                                border: 1px solid #ddd; 
                                border-radius: 8px; 
                                padding: 12px; 
                                margin: 8px 0; 
                                background-color: white;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="color: #333;">{demo['titulo']}</strong>
                                    <span style="color: {prioridad_color[demo['prioridad']]}; font-size: 12px;">
                                        {prioridad_icon[demo['prioridad']]} {demo['prioridad'].upper()}
                                    </span>
                                </div>
                        """, unsafe_allow_html=True)
                        
                        if demo['descripcion']:
                            st.markdown(f"<small style='color: #666;'>{demo['descripcion'][:100]}...</small>", unsafe_allow_html=True)
                        
                        if demo['institucion_nombre']:
                            st.markdown(f"🏫 **Institución:** {demo['institucion_nombre']}")
                        
                        if demo['responsable']:
                            st.markdown(f"👤 **Responsable:** {demo['responsable']}")
                        
                        if demo['fecha_limite']:
                            fecha_limite = datetime.datetime.strptime(demo['fecha_limite'], "%Y-%m-%d").date()
                            dias_restantes = (fecha_limite - datetime.date.today()).days
                            color_fecha = "#DC3545" if dias_restantes < 0 else "#FFC107" if dias_restantes < 7 else "#28A745"
                            st.markdown(f"📅 **Límite:** <span style='color: {color_fecha};'>{fecha_limite}</span>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Botones de acción
                        col_edit, col_move, col_delete = st.columns([1, 2, 1])
                        
                        with col_edit:
                            if st.button("✏️", key=f"edit_{demo['id']}", help="Editar"):
                                st.session_state[f"editing_{demo['id']}"] = True
                        
                        with col_move:
                            nuevo_estado = st.selectbox(
                                "Mover a:",
                                [s for s in estados_keys if s != estado],
                                key=f"move_{demo['id']}",
                                label_visibility="collapsed"
                            )
                            if st.button("Mover", key=f"move_btn_{demo['id']}"):
                                demos.cambiar_estado_demo(conn, demo['id'], nuevo_estado)
                                st.success(f"Demo movida a {estados[nuevo_estado]['title']}")
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{demo['id']}", help="Eliminar"):
                                demos.delete_demo(conn, demo['id'])
                                st.success("Demo eliminada")
                                st.rerun()
                        
                        # Modal de edición
                        if st.session_state.get(f"editing_{demo['id']}", False):
                            with st.form(f"edit_demo_{demo['id']}"):
                                st.markdown(f"### Editando: {demo['titulo']}")
                                
                                nuevo_titulo = st.text_input("Título", value=demo['titulo'])
                                nueva_descripcion = st.text_area("Descripción", value=demo['descripcion'] or "")
                                nueva_prioridad = st.selectbox("Prioridad", ["baja", "media", "alta"], 
                                                             index=["baja", "media", "alta"].index(demo['prioridad']))
                                
                                # Selector de institución para edición
                                inst_actual = demo['institucion_nombre'] if demo['institucion_nombre'] else "Sin asignar"
                                inst_index = 0
                                if inst_actual != "Sin asignar":
                                    for idx, inst_opt in enumerate(inst_options):
                                        if inst_actual in inst_opt:
                                            inst_index = idx
                                            break
                                
                                nueva_institucion = st.selectbox("Institución", inst_options, index=inst_index)
                                nuevo_responsable = st.text_input("Responsable", value=demo['responsable'] or "")
                                
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.form_submit_button("Guardar cambios", type="primary"):
                                        # Procesar nueva institución
                                        nueva_institucion_id = None
                                        if nueva_institucion != "Sin asignar":
                                            for inst in insts:
                                                if f"{inst['nombre']} (ID: {inst['id']})" == nueva_institucion:
                                                    nueva_institucion_id = inst['id']
                                                    break
                                        
                                        demos.update_demo(conn, demo['id'],
                                                        titulo=nuevo_titulo,
                                                        descripcion=nueva_descripcion,
                                                        prioridad=nueva_prioridad,
                                                        institucion_id=nueva_institucion_id,
                                                        responsable=nuevo_responsable if nuevo_responsable else None)
                                        
                                        del st.session_state[f"editing_{demo['id']}"]
                                        st.success("Demo actualizada exitosamente!")
                                        st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("Cancelar"):
                                        del st.session_state[f"editing_{demo['id']}"]
                                        st.rerun()

def dashboard_selector(conn):
    st.sidebar.markdown("## Gestión de datos")
    seccion = st.sidebar.selectbox(
        "Selecciona módulo",
        ["Dashboard", "Usuarios", "Instituciones", "Participantes", "Fases Completadas", "Gestión de Demos"]
    )
    if seccion == "Dashboard":
        st.header("Resumen")
        data = get_dashboard_data(conn, None)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Instituciones", data["instituciones"])
        with col2:
            st.metric("Participantes", data["participantes"])
        with col3:
            st.metric("Fases Completadas", data["fases_completadas"])
        with col4:
            # Añadir métricas de demos
            try:
                demo_stats = demos.get_demos_estadisticas(conn)
                st.metric("Demos Activas", demo_stats["total"])
            except:
                st.metric("Demos Activas", 0)
    elif seccion == "Usuarios":
        crud_usuarios(conn)
    elif seccion == "Instituciones":
        crud_instituciones(conn)
    elif seccion == "Participantes":
        crud_participantes(conn)
    elif seccion == "Fases Completadas":
        crud_fases_completadas(conn)
    elif seccion == "Gestión de Demos":
        gestión_demos_kanban(conn)
