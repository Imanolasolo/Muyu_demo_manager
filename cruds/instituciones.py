import sqlite3

def create_institucion(conn, nombre, responsable, email_responsable, telefono_responsable=None, estado='en_progreso', fecha_inicio=None, fecha_fin=None, ciudad=None, pais=None, responsable_comercial=None):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO instituciones (nombre, responsable, email_responsable, telefono_responsable, estado, fecha_inicio, fecha_fin, ciudad, pais, responsable_comercial) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (nombre, responsable, email_responsable, telefono_responsable, estado, fecha_inicio, fecha_fin, ciudad, pais, responsable_comercial)
    )
    conn.commit()
    return cur.lastrowid

def get_institucion_by_id(conn, institucion_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM instituciones WHERE id = ?", (institucion_id,))
    return cur.fetchone()

def update_institucion(conn, institucion_id, **kwargs):
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        values.append(value)
    values.append(institucion_id)
    sql = f"UPDATE instituciones SET {', '.join(fields)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def delete_institucion(conn, institucion_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM instituciones WHERE id = ?", (institucion_id,))
    conn.commit()
    return cur.rowcount

def list_instituciones(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM instituciones")
    return cur.fetchall()
