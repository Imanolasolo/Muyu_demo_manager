import sqlite3

def create_agrupador(conn, nombre, descripcion=None):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO agrupadores (nombre, descripcion) VALUES (?, ?)",
        (nombre, descripcion)
    )
    conn.commit()
    return cur.lastrowid

def get_agrupador_by_id(conn, agrupador_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM agrupadores WHERE id = ?", (agrupador_id,))
    return cur.fetchone()

def update_agrupador(conn, agrupador_id, **kwargs):
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(agrupador_id)
    sql = f"UPDATE agrupadores SET {', '.join(fields)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def delete_agrupador(conn, agrupador_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM agrupadores WHERE id = ?", (agrupador_id,))
    conn.commit()
    return cur.rowcount

def list_agrupadores(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM agrupadores")
    return cur.fetchall()
