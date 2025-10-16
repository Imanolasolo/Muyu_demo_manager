import sqlite3
from typing import List, Dict, Optional

def crear_tarea_demo(conn, demo_id: int, descripcion: str, responsable: str = None):
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO tareas_demo (demo_id, descripcion, responsable, completada)
        VALUES (?, ?, ?, 0)
    ''', (demo_id, descripcion, responsable))
    conn.commit()
    return cur.lastrowid

def listar_tareas_demo(conn, demo_id: int) -> List[Dict]:
    cur = conn.cursor()
    cur.execute('''
        SELECT * FROM tareas_demo WHERE demo_id = ? ORDER BY fecha_creacion DESC
    ''', (demo_id,))
    return [dict(row) for row in cur.fetchall()]

def marcar_tarea_completada(conn, tarea_id: int, completada: bool):
    cur = conn.cursor()
    if completada:
        cur.execute('''
            UPDATE tareas_demo SET completada = 1, fecha_completada = CURRENT_TIMESTAMP WHERE id = ?
        ''', (tarea_id,))
    else:
        cur.execute('''
            UPDATE tareas_demo SET completada = 0, fecha_completada = NULL WHERE id = ?
        ''', (tarea_id,))
    conn.commit()

def eliminar_tarea_demo(conn, tarea_id: int):
    cur = conn.cursor()
    cur.execute('DELETE FROM tareas_demo WHERE id = ?', (tarea_id,))
    conn.commit()
