import sqlite3

def create_usuario(conn, nombre, email, password, rol):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
        (nombre, email, password, rol)
    )
    conn.commit()
    return cur.lastrowid

def get_usuario_by_id(conn, usuario_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    return cur.fetchone()

def get_usuario_by_email(conn, email):
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    return cur.fetchone()

def update_usuario(conn, usuario_id, nombre=None, email=None, password=None, rol=None):
    fields = []
    values = []
    if nombre:
        fields.append("nombre = ?")
        values.append(nombre)
    if email:
        fields.append("email = ?")
        values.append(email)
    if password:
        fields.append("password = ?")
        values.append(password)
    if rol:
        fields.append("rol = ?")
        values.append(rol)
    values.append(usuario_id)
    sql = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.rowcount

def delete_usuario(conn, usuario_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    return cur.rowcount

def list_usuarios(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    return cur.fetchall()
