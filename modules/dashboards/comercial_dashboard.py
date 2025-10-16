def show(st, conn, user):
    st.title("Dashboard Comercial")
    from cruds import demos
    import streamlit as st
    import math

    fases = demos.get_fases_disponibles(conn)
    todas_demos = demos.list_demos(conn)
    demos_usuario = [d for d in todas_demos if d.get("responsable") == user["nombre"]]

    # Filtro por fase
    fase_opciones = ["Todas"] + [f["nombre"] for f in fases]
    fase_seleccionada = st.selectbox("Filtrar por fase", fase_opciones)
    if fase_seleccionada != "Todas":
        demos_usuario = [d for d in demos_usuario if d.get("fase_nombre") == fase_seleccionada]

    # Paginación
    page_size = 10
    total = len(demos_usuario)
    total_pages = math.ceil(total / page_size)
    page = st.number_input("Página", min_value=1, max_value=max(total_pages,1), value=1, step=1)
    start = (page-1)*page_size
    end = start+page_size
    demos_pagina = demos_usuario[start:end]

    # Mostrar como tarjetas sencillas tipo Kanban con campo editable 'Estado'
    if demos_pagina:
        for demo in demos_pagina:
            with st.container():
                st.markdown(f"""
                    <div style='background:#f7f7fa;padding:10px;margin-bottom:10px;border-radius:8px;box-shadow:0 1px 2px #ddd;'>
                        <b>{demo['titulo']}</b><br>
                        <span style='font-size:12px;'>{demo.get('descripcion','')}</span><br>
                        <span style='font-size:12px;'><b>Institución:</b> {demo.get('institucion_nombre','')}</span><br>
                        <span style='font-size:12px;'><b>Fase:</b> {demo.get('fase_nombre','')}</span><br>
                        <span style='font-size:12px;'><b>Prioridad:</b> {demo.get('prioridad','')}</span><br>
                    </div>
                """, unsafe_allow_html=True)
                # Campo editable Estado
                estado_actual = demo.get('estado', '')
                nuevo_estado = st.text_input("Estado", value=estado_actual or "", key=f"estado_{demo['id']}")
                if nuevo_estado != estado_actual:
                    if st.button("Guardar estado", key=f"guardar_estado_{demo['id']}"):
                        demos.update_demo(conn, demo['id'], estado=nuevo_estado)
                        st.success("Estado actualizado")
        st.caption(f"Mostrando {start+1}-{min(end,total)} de {total} demos")
    else:
        st.info("No hay demos asignadas para mostrar.")
