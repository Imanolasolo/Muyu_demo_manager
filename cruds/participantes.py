import sqlite3

def create_participante(conn, institucion_id, nombre, rol, email=None, telefono=None):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO participantes (institucion_id, nombre, rol, email, telefono) VALUES (?, ?, ?, ?, ?)",
        (institucion_id, nombre, rol, email, telefono)
    )
    conn.commit()
    return cur.lastrowid

def get_participante_by_id(conn, participante_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM participantes WHERE id = ?", (participante_id,))
    return cur.fetchone()

def update_participante(conn, participante_id, **kwargs):
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(participante_id)
    sql = f"UPDATE participantes SET {', '.join(fields)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def delete_participante(conn, participante_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM participantes WHERE id = ?", (participante_id,))
    conn.commit()
    return cur.rowcount

def list_participantes(conn, institucion_id=None):
    cur = conn.cursor()
    if institucion_id:
        cur.execute("SELECT * FROM participantes WHERE institucion_id = ?", (institucion_id,))
    else:
        cur.execute("SELECT * FROM participantes")
    return cur.fetchall()
