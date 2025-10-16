import sqlite3

def create_table_tareas_demo():
    conn = sqlite3.connect('db/muyudemo.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tareas_demo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demo_id INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            responsable TEXT,
            completada INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_completada TIMESTAMP,
            FOREIGN KEY (demo_id) REFERENCES demos(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table_tareas_demo()
    print("Tabla tareas_demo creada o ya existente.")
