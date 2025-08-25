import sqlite3

def create_fase_institucion(conn, institucion_id, fase_id, estado='pendiente', responsable=None):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO fases_institucion (institucion_id, fase_id, estado, responsable) VALUES (?, ?, ?, ?)",
        (institucion_id, fase_id, estado, responsable)
    )
    conn.commit()
    return cur.lastrowid

def get_fase_institucion_by_id(conn, fase_inst_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM fases_institucion WHERE id = ?", (fase_inst_id,))
    return cur.fetchone()

def update_fase_institucion(conn, fase_inst_id, **kwargs):
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(fase_inst_id)
    sql = f"UPDATE fases_institucion SET {', '.join(fields)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def delete_fase_institucion(conn, fase_inst_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM fases_institucion WHERE id = ?", (fase_inst_id,))
    conn.commit()
    return cur.rowcount

def list_fases_institucion(conn, institucion_id=None):
    cur = conn.cursor()
    if institucion_id:
        cur.execute("SELECT * FROM fases_institucion WHERE institucion_id = ?", (institucion_id,))
    else:
        cur.execute("SELECT * FROM fases_institucion")
    return cur.fetchall()
