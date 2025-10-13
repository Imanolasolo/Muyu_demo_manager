import sqlite3
import os

# Nombre de la base de datos
DB_NAME = "db/muyudemo.db"

def add_demos_table():
    """Añadir la tabla de demos si no existe"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Verificar si la tabla ya existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='demos'")
    exists = c.fetchone()
    
    if not exists:
        print("🔧 Creando tabla de demos...")
        # Tabla de demos para gestión kanban
        c.execute("""
        CREATE TABLE IF NOT EXISTS demos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'en_progreso', 'completado', 'cancelado')),
            institucion_id INTEGER,
            responsable TEXT,
            prioridad TEXT DEFAULT 'media' CHECK(prioridad IN ('baja', 'media', 'alta')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_limite DATE,
            FOREIGN KEY (institucion_id) REFERENCES instituciones(id) ON DELETE SET NULL
        )
        """)
        
        # Insertar algunas demos de ejemplo
        demos_ejemplo = [
            ("Demo Colegio San Patricio", "Implementación inicial de Muyu App para docentes de primaria", "pendiente", None, "Admin", "alta"),
            ("Demo Universidad Nacional", "Piloto con profesores de ingeniería", "en_progreso", None, "Admin", "media"),
            ("Demo Instituto Tecnológico", "Evaluación de herramientas de grabación", "completado", None, "Admin", "baja"),
        ]
        
        for titulo, desc, estado, inst_id, resp, prioridad in demos_ejemplo:
            c.execute("""
                INSERT INTO demos (titulo, descripcion, estado, institucion_id, responsable, prioridad)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (titulo, desc, estado, inst_id, resp, prioridad))
        
        conn.commit()
        print("✅ Tabla de demos creada con datos de ejemplo.")
    else:
        print("ℹ️ La tabla de demos ya existe.")
    
    conn.close()

if __name__ == "__main__":
    add_demos_table()
    print("✅ Base de datos actualizada.")