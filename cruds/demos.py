import sqlite3
from typing import List, Dict, Optional

def create_demo(conn, titulo: str, descripcion: str = None, fase_id: int = None, 
                institucion_id: int = None, responsable: str = None, prioridad: str = "media", estado: str = "pendiente"):
    """Crear una nueva demo"""
    cur = conn.cursor()
    # Si no se especifica fase, usar la primera fase disponible
    if fase_id is None:
        cur.execute("SELECT id FROM fases ORDER BY orden LIMIT 1")
        result = cur.fetchone()
        fase_id = result['id'] if result else 1
    cur.execute("""
        INSERT INTO demos (titulo, descripcion, estado, fase_id, institucion_id, responsable, prioridad)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (titulo, descripcion, estado, fase_id, institucion_id, responsable, prioridad))
    conn.commit()
    return cur.lastrowid

def list_demos(conn) -> List[Dict]:
    """Listar todas las demos"""
    cur = conn.cursor()
    cur.execute("""
        SELECT d.*, i.nombre as institucion_nombre, f.nombre as fase_nombre, f.orden as fase_orden
        FROM demos d 
        LEFT JOIN instituciones i ON d.institucion_id = i.id
        LEFT JOIN fases f ON d.fase_id = f.id
        ORDER BY d.fecha_creacion DESC
    """)
    return [dict(row) for row in cur.fetchall()]

def list_demos_by_fase(conn, fase_id: int) -> List[Dict]:
    """Listar demos por fase"""
    cur = conn.cursor()
    cur.execute("""
        SELECT d.*, i.nombre as institucion_nombre, f.nombre as fase_nombre, f.orden as fase_orden
        FROM demos d 
        LEFT JOIN instituciones i ON d.institucion_id = i.id
        LEFT JOIN fases f ON d.fase_id = f.id
        WHERE d.fase_id = ?
        ORDER BY d.fecha_creacion DESC
    """, (fase_id,))
    return [dict(row) for row in cur.fetchall()]

def update_demo(conn, demo_id: int, **kwargs):
    """Actualizar una demo"""
    if not kwargs:
        return
    
    # Construir la consulta dinámicamente
    set_clauses = []
    values = []
    
    for key, value in kwargs.items():
        if key in ['titulo', 'descripcion', 'fase_id', 'institucion_id', 'responsable', 'prioridad', 'fecha_limite', 'estado']:
            set_clauses.append(f"{key} = ?")
            values.append(value)
    
    if set_clauses:
        values.append(demo_id)
        query = f"UPDATE demos SET {', '.join(set_clauses)}, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?"
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()

def delete_demo(conn, demo_id: int):
    """Eliminar una demo"""
    cur = conn.cursor()
    cur.execute("DELETE FROM demos WHERE id = ?", (demo_id,))
    conn.commit()

def get_demo_by_id(conn, demo_id: int) -> Optional[Dict]:
    """Obtener una demo por ID"""
    cur = conn.cursor()
    cur.execute("""
        SELECT d.*, i.nombre as institucion_nombre, f.nombre as fase_nombre, f.orden as fase_orden
        FROM demos d 
        LEFT JOIN instituciones i ON d.institucion_id = i.id
        LEFT JOIN fases f ON d.fase_id = f.id
        WHERE d.id = ?
    """, (demo_id,))
    row = cur.fetchone()
    return dict(row) if row else None

def get_demos_estadisticas(conn) -> Dict:
    """Obtener estadísticas de demos"""
    cur = conn.cursor()
    
    # Contar demos por fase
    cur.execute("""
        SELECT f.nombre, COUNT(*) as count 
        FROM demos d 
        LEFT JOIN fases f ON d.fase_id = f.id 
        GROUP BY f.nombre
    """)
    fases = dict(cur.fetchall())
    
    # Total de demos
    cur.execute("SELECT COUNT(*) as total FROM demos")
    total = cur.fetchone()["total"]
    
    return {
        "total": total,
        "por_fases": fases
    }

def cambiar_fase_demo(conn, demo_id: int, nueva_fase_id: int):
    """Cambiar la fase de una demo específica"""
    cur = conn.cursor()
    cur.execute("""
        UPDATE demos 
        SET fase_id = ?, fecha_actualizacion = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (nueva_fase_id, demo_id))
    conn.commit()

def get_fases_disponibles(conn) -> List[Dict]:
    """Obtener todas las fases disponibles"""
    cur = conn.cursor()
    cur.execute("SELECT * FROM fases ORDER BY orden")
    return [dict(row) for row in cur.fetchall()]