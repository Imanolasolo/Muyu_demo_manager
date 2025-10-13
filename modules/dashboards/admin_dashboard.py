import streamlit as st
from cruds import instituciones, participantes, usuarios, demos
import datetime
def show(st, conn, user):
    st.title("Dashboard Administrador")
    st.sidebar.title("Menú")
    menu_options = ["Gestión de Usuarios", "Gestión de Instituciones", "Gestión de Participantes", "Gestión de Fases", "Gestión de Demos"]
    choice = st.sidebar.selectbox("Selecciona una opción", menu_options)

    if choice == "Gestión de Usuarios":
        crud_usuarios(conn)
    elif choice == "Gestión de Instituciones":
        crud_instituciones(conn)
    elif choice == "Gestión de Participantes":
        crud_participantes(conn)
    elif choice == "Gestión de Fases":
        crud_fases(conn)
    elif choice == "Gestión de Demos":
        gestión_demos_kanban(conn)


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
    st.header("Gestión de Usuarios")
    option = st.selectbox("Acción", ["Listar Usuarios", "Crear Usuario", "Actualizar Usuario", "Eliminar Usuario"])
    if option == "Listar Usuarios":
        data = usuarios.list_usuarios(conn)
        st.dataframe([dict(row) for row in data])
    elif option == "Crear Usuario":
    
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
    elif option == "Actualizar Usuario":
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
    elif option == "Eliminar Usuario":
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

def crud_fases(conn):
    """CRUD operations for the 'fases' table."""
    st.subheader("Gestión de Fases")
    action = st.selectbox("Acción", ["Listar", "Crear", "Actualizar", "Eliminar"], key="fases_action")
    
    if action == "Listar":
        c = conn.cursor()
        c.execute("SELECT * FROM fases ORDER BY orden")
        data = c.fetchall()
        st.dataframe([dict(row) for row in data])
    
    elif action == "Crear":
        with st.form("crear_fase"):
            nombre = st.text_input("Nombre de la fase")
            descripcion = st.text_area("Descripción")
            orden = st.number_input("Orden", min_value=1, step=1)
            submitted = st.form_submit_button("Crear")
            if submitted:
                c = conn.cursor()
                c.execute("INSERT INTO fases (nombre, descripcion, orden) VALUES (?, ?, ?)",
                          (nombre, descripcion, orden))
                conn.commit()
                st.success("Fase creada")
    
    elif action == "Actualizar":
        c = conn.cursor()
        c.execute("SELECT * FROM fases ORDER BY orden")
        fases = c.fetchall()
        fase_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in fases}
        selected_fase = st.selectbox("Selecciona fase", list(fase_dict.keys()), key="upd_fase_select")
        if selected_fase:
            fase_id = fase_dict[selected_fase]
            nombre = st.text_input("Nuevo nombre")
            descripcion = st.text_area("Nueva descripción")
            orden = st.number_input("Nuevo orden", min_value=1, step=1)
            if st.button("Actualizar fase"):
                fields = {}
                if nombre: fields["nombre"] = nombre
                if descripcion: fields["descripcion"] = descripcion
                if orden: fields["orden"] = orden
                if fields:
                    set_clause = ", ".join(f"{key} = ?" for key in fields.keys())
                    values = list(fields.values()) + [fase_id]
                    c.execute(f"UPDATE fases SET {set_clause} WHERE id = ?", values)
                    conn.commit()
                    st.success("Fase actualizada")
    
    elif action == "Eliminar":
        c = conn.cursor()
        c.execute("SELECT * FROM fases ORDER BY orden")
        fases = c.fetchall()
        fase_dict = {f"{row['nombre']} (ID {row['id']})": row['id'] for row in fases}
        selected_fase = st.selectbox("Selecciona fase", list(fase_dict.keys()), key="del_fase_select")
        if selected_fase:
            fase_id = fase_dict[selected_fase]
            if st.button("Eliminar fase"):
                c.execute("DELETE FROM fases WHERE id = ?", (fase_id,))
                conn.commit()
                st.success("Fase eliminada")

def gestión_demos_kanban(conn):
    """Panel Kanban para gestión de demos"""
    st.subheader("🎯 Gestión de Demos - Panel Kanban")
    
    # Estadísticas generales
    stats = demos.get_demos_estadisticas(conn)
    
    # Crear métricas dinámicas basadas en las fases
    fases_stats = stats.get("por_fases", {})
    
    # Mostrar métricas en columnas
    if fases_stats:
        num_cols = min(len(fases_stats) + 1, 6)  # Máximo 6 columnas
        cols = st.columns(num_cols)
        
        with cols[0]:
            st.metric("📝 Total", stats["total"])
        
        for i, (fase_nombre, cantidad) in enumerate(fases_stats.items(), 1):
            if i < num_cols:
                with cols[i]:
                    # Truncar nombre si es muy largo
                    nombre_corto = fase_nombre[:15] + "..." if len(fase_nombre) > 15 else fase_nombre
                    st.metric(f"📋 {nombre_corto}", cantidad)
    else:
        st.metric("📝 Total", stats["total"])
    
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
                
                # Selector de fase inicial
                fases_disponibles = demos.get_fases_disponibles(conn)
                fase_options = [f"{fase['nombre']}" for fase in fases_disponibles]
                fase_selected = st.selectbox("Fase inicial", fase_options, index=0)
                
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
                
                # Procesar fase
                fase_id = None
                for fase in fases_disponibles:
                    if fase['nombre'] == fase_selected:
                        fase_id = fase['id']
                        break
                
                demos.create_demo(conn, titulo, descripcion, fase_id, institucion_id, responsable, prioridad)
                st.success("Demo creada exitosamente!")
                st.rerun()
    
    st.divider()
    
    # Panel Kanban
    st.markdown("### 📋 Tablero Kanban")
    
    # Obtener todas las fases disponibles
    todas_las_fases = demos.get_fases_disponibles(conn)
    
    if not todas_las_fases:
        st.error("No hay fases configuradas. Por favor, configure las fases primero.")
        return
    
    # Filtros y configuración del kanban
    st.markdown("#### 🔍 Filtros y Configuración")
    
    col_filtros1, col_filtros2, col_filtros3 = st.columns(3)
    
    with col_filtros1:
        # Filtro para seleccionar qué fases mostrar
        nombres_fases = [fase['nombre'] for fase in todas_las_fases]
        fases_seleccionadas = st.multiselect(
            "📋 Seleccionar fases a mostrar:",
            nombres_fases,
            default=nombres_fases,  # Por defecto todas seleccionadas
            key="fases_filtro"
        )
    
    with col_filtros2:
        # Filtro por prioridad
        prioridades_disponibles = ["Todas", "alta", "media", "baja"]
        prioridad_filtro = st.selectbox(
            "⚡ Filtrar por prioridad:",
            prioridades_disponibles,
            key="prioridad_filtro"
        )
    
    with col_filtros3:
        # Configuración de columnas por fila
        max_cols = min(len(fases_seleccionadas), 6) if fases_seleccionadas else 4
        cols_por_fila = st.selectbox(
            "📱 Columnas por fila:",
            options=[2, 3, 4, 5, 6],
            index=2,  # 4 columnas por defecto
            key="cols_por_fila"
        )
    
    # Fila adicional de filtros
    col_filtros4, col_filtros5 = st.columns(2)
    
    with col_filtros4:
        # Filtro por responsable
        todos_demos = demos.list_demos(conn)
        responsables_unicos = list(set([demo['responsable'] for demo in todos_demos if demo['responsable']]))
        responsables_options = ["Todos"] + responsables_unicos
        responsable_filtro = st.selectbox(
            "👤 Filtrar por responsable:",
            responsables_options,
            key="responsable_filtro"
        )
    
    with col_filtros5:
        # Búsqueda por título
        busqueda_titulo = st.text_input(
            "🔍 Buscar por título:",
            placeholder="Escribe para buscar...",
            key="busqueda_titulo"
        )
    
    # Filtrar fases según selección
    if fases_seleccionadas:
        fases_disponibles = [fase for fase in todas_las_fases if fase['nombre'] in fases_seleccionadas]
    else:
        fases_disponibles = todas_las_fases
        st.warning("⚠️ No hay fases seleccionadas. Mostrando todas las fases disponibles.")
    
    # Mostrar resumen de filtros aplicados
    if prioridad_filtro != "Todas" or responsable_filtro != "Todos" or busqueda_titulo or len(fases_seleccionadas) != len(todas_las_fases):
        st.markdown("#### 🎯 Filtros Aplicados:")
        filtros_info = []
        if len(fases_seleccionadas) != len(todas_las_fases):
            filtros_info.append(f"📋 Fases: {len(fases_seleccionadas)}/{len(todas_las_fases)} seleccionadas")
        if prioridad_filtro != "Todas":
            filtros_info.append(f"⚡ Prioridad: {prioridad_filtro}")
        if responsable_filtro != "Todos":
            filtros_info.append(f"👤 Responsable: {responsable_filtro}")
        if busqueda_titulo:
            filtros_info.append(f"🔍 Búsqueda: '{busqueda_titulo}'")
        
        st.info(" | ".join(filtros_info))
    
    st.divider()
    
    # Mostrar fases en grupos según configuración
    num_fases = len(fases_disponibles)
    
    if num_fases == 0:
        st.info("No hay fases para mostrar con los filtros actuales.")
        return
    
    # Dividir fases en grupos según cols_por_fila
    total_grupos = (num_fases + cols_por_fila - 1) // cols_por_fila
    
    for grupo_idx in range(total_grupos):
        i = grupo_idx * cols_por_fila
        grupo_fases = fases_disponibles[i:i + cols_por_fila]
        
        # Añadir separador entre grupos si hay más de un grupo
        if grupo_idx > 0:
            st.markdown("---")
            st.markdown(f"#### Grupo {grupo_idx + 1}")
        
        cols = st.columns(len(grupo_fases))
    
        # Configuración de colores para las fases
        colores_fases = [
            "#007BFF",  # Azul
            "#FFA500",  # Naranja  
            "#28A745",  # Verde
            "#DC3545",  # Rojo
            "#6F42C1",  # Púrpura
            "#20C997",  # Teal
            "#FFC107",  # Amarillo
            "#6C757D"   # Gris
        ]
        
        for j, (fase, col) in enumerate(zip(grupo_fases, cols)):
            with col:
                # Usar índice global para los colores
                color_idx = (i + j) % len(colores_fases)
                color = colores_fases[color_idx]
                fase_nombre_corto = fase['nombre'][:20] + "..." if len(fase['nombre']) > 20 else fase['nombre']
                
                st.markdown(f"""
                    <div style="
                        background-color: {color}20; 
                        border-left: 4px solid {color}; 
                        padding: 10px; 
                        border-radius: 5px; 
                        margin-bottom: 10px;
                    ">
                        <h4 style="margin: 0; color: {color}; font-size: 14px;">
                            📋 {fase_nombre_corto}
                        </h4>
                    </div>
                """, unsafe_allow_html=True)
                
                # Obtener demos de esta fase
                demos_fase = demos.list_demos_by_fase(conn, fase['id'])
                
                # Aplicar filtros
                if prioridad_filtro != "Todas":
                    demos_fase = [demo for demo in demos_fase if demo['prioridad'] == prioridad_filtro]
                
                if responsable_filtro != "Todos":
                    demos_fase = [demo for demo in demos_fase if demo['responsable'] == responsable_filtro]
                
                if busqueda_titulo:
                    demos_fase = [demo for demo in demos_fase if busqueda_titulo.lower() in demo['titulo'].lower()]
                
                if not demos_fase:
                    # Mensaje personalizado según filtros activos
                    filtros_activos = []
                    if prioridad_filtro != "Todas":
                        filtros_activos.append(f"prioridad '{prioridad_filtro}'")
                    if responsable_filtro != "Todos":
                        filtros_activos.append(f"responsable '{responsable_filtro}'")
                    if busqueda_titulo:
                        filtros_activos.append(f"título que contenga '{busqueda_titulo}'")
                    
                    if filtros_activos:
                        st.info(f"No hay demos en esta fase con: {', '.join(filtros_activos)}")
                    else:
                        st.info("No hay demos en esta fase")
                else:
                    for demo in demos_fase:
                        # Crear tarjeta expandible para cada demo
                        prioridad_color = {"alta": "#DC3545", "media": "#FFC107", "baja": "#6C757D"}
                        prioridad_icon = {"alta": "🔴", "media": "🟡", "baja": "🟢"}
                        
                        # Título del expander con información resumida
                        titulo_expander = f"{prioridad_icon[demo['prioridad']]} {demo['titulo']}"
                        if demo['responsable']:
                            titulo_expander += f" | 👤 {demo['responsable']}"
                        
                        with st.expander(titulo_expander, expanded=False):
                            # Crear formulario de edición dentro del expander
                            with st.form(f"demo_form_{demo['id']}"):
                                st.markdown(f"**📝 Demo ID:** {demo['id']}")
                            
                                # Campos editables
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    nuevo_titulo = st.text_input("📌 Título:", value=demo['titulo'], key=f"titulo_{demo['id']}")
                                    nueva_prioridad = st.selectbox("⚡ Prioridad:", ["baja", "media", "alta"], 
                                                                 index=["baja", "media", "alta"].index(demo['prioridad']),
                                                                 key=f"prioridad_{demo['id']}")
                                    
                                    # Selector de institución
                                    insts = instituciones.list_instituciones(conn)
                                    inst_options = ["Sin asignar"] + [f"{inst['nombre']} (ID: {inst['id']})" for inst in insts]
                                    inst_actual = demo['institucion_nombre'] if demo['institucion_nombre'] else "Sin asignar"
                                    inst_index = 0
                                    if inst_actual != "Sin asignar":
                                        for idx, inst_opt in enumerate(inst_options):
                                            if inst_actual in inst_opt:
                                                inst_index = idx
                                                break
                                    nueva_institucion = st.selectbox("🏫 Institución:", inst_options, index=inst_index, key=f"inst_{demo['id']}")
                                
                                with col2:
                                    nuevo_responsable = st.text_input("👤 Responsable:", value=demo['responsable'] or "", key=f"resp_{demo['id']}")
                                    
                                    # Selector de fase
                                    todas_las_fases_form = demos.get_fases_disponibles(conn)
                                    fase_names = [f['nombre'] for f in todas_las_fases_form]
                                    fase_actual_index = 0
                                    if demo.get('fase_nombre'):
                                        try:
                                            fase_actual_index = fase_names.index(demo['fase_nombre'])
                                        except ValueError:
                                            pass
                                    nueva_fase_sel = st.selectbox("📋 Fase:", fase_names, index=fase_actual_index, key=f"fase_{demo['id']}")
                                    
                                    # Fecha límite
                                    fecha_actual = None
                                    if demo.get('fecha_limite'):
                                        try:
                                            fecha_actual = datetime.datetime.strptime(demo['fecha_limite'], "%Y-%m-%d").date()
                                        except:
                                            pass
                                    nueva_fecha_limite = st.date_input("📅 Fecha límite:", value=fecha_actual, key=f"fecha_{demo['id']}")
                                
                                # Descripción completa
                                nueva_descripcion = st.text_area("📄 Descripción:", value=demo['descripcion'] or "", height=100, key=f"desc_{demo['id']}")
                            
                                # Información adicional (solo lectura)
                                col_info1, col_info2 = st.columns(2)
                                with col_info1:
                                    if demo.get('fecha_creacion'):
                                        st.info(f"📅 Creado: {demo['fecha_creacion']}")
                                with col_info2:
                                    if demo.get('fecha_actualizacion'):
                                        st.info(f"🔄 Actualizado: {demo['fecha_actualizacion']}")
                                
                                # Mostrar días restantes si hay fecha límite
                                if nueva_fecha_limite:
                                    dias_restantes = (nueva_fecha_limite - datetime.date.today()).days
                                    if dias_restantes < 0:
                                        st.error(f"⚠️ Vencido hace {abs(dias_restantes)} días")
                                    elif dias_restantes == 0:
                                        st.warning("⏰ Vence hoy")
                                    elif dias_restantes <= 7:
                                        st.warning(f"⏳ Vence en {dias_restantes} días")
                                    else:
                                        st.success(f"✅ {dias_restantes} días restantes")
                                
                                # Botones de acción
                                col_save, col_move, col_delete = st.columns(3)
                            
                                with col_save:
                                    if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                        # Procesar nueva institución
                                        nueva_institucion_id = None
                                        if nueva_institucion != "Sin asignar":
                                            for inst in insts:
                                                if f"{inst['nombre']} (ID: {inst['id']})" == nueva_institucion:
                                                    nueva_institucion_id = inst['id']
                                                    break
                                        
                                        # Procesar nueva fase
                                        nueva_fase_id = None
                                        for f in todas_las_fases_form:
                                            if f['nombre'] == nueva_fase_sel:
                                                nueva_fase_id = f['id']
                                                break
                                        
                                        # Actualizar demo
                                        demos.update_demo(conn, demo['id'],
                                                        titulo=nuevo_titulo,
                                                        descripcion=nueva_descripcion,
                                                        prioridad=nueva_prioridad,
                                                        fase_id=nueva_fase_id,
                                                        institucion_id=nueva_institucion_id,
                                                        responsable=nuevo_responsable if nuevo_responsable else None,
                                                        fecha_limite=nueva_fecha_limite.strftime('%Y-%m-%d') if nueva_fecha_limite else None)
                                        
                                        st.success("✅ Demo actualizada exitosamente!")
                                        st.rerun()
                                
                                with col_move:
                                    # Mover a otra fase
                                    otras_fases = [f for f in todas_las_fases_form if f['nombre'] != nueva_fase_sel]
                                    if otras_fases and st.form_submit_button("🔄 Mover Fase", use_container_width=True):
                                        # Mover a la siguiente fase (o primera disponible)
                                        siguiente_fase = otras_fases[0]
                                        demos.cambiar_fase_demo(conn, demo['id'], siguiente_fase['id'])
                                        st.success(f"📋 Demo movida a: {siguiente_fase['nombre']}")
                                        st.rerun()
                                
                                with col_delete:
                                    if st.form_submit_button("🗑️ Eliminar", type="secondary", use_container_width=True):
                                        demos.delete_demo(conn, demo['id'])
                                        st.success("🗑️ Demo eliminada")
                                        st.rerun()

