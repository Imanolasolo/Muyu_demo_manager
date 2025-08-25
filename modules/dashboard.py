import streamlit as st
from cruds import usuarios, instituciones, participantes, fases_completadas

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
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed = pwd_context.hash(password)
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
                    from passlib.context import CryptContext
                    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                    fields["password"] = pwd_context.hash(password)
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

def dashboard_selector(conn):
    st.sidebar.markdown("## Gestión de datos")
    seccion = st.sidebar.selectbox(
        "Selecciona módulo",
        ["Dashboard", "Usuarios", "Instituciones", "Participantes", "Fases Completadas"]
    )
    if seccion == "Dashboard":
        st.header("Resumen")
        data = get_dashboard_data(conn, None)
        st.metric("Instituciones", data["instituciones"])
        st.metric("Participantes", data["participantes"])
        st.metric("Fases Completadas", data["fases_completadas"])
    elif seccion == "Usuarios":
        crud_usuarios(conn)
    elif seccion == "Instituciones":
        crud_instituciones(conn)
    elif seccion == "Participantes":
        crud_participantes(conn)
    elif seccion == "Fases Completadas":
        crud_fases_completadas(conn)
