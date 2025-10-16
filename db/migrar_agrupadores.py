import sqlite3

DB_NAME = "db/muyudemo.db"

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Crear tabla agrupadores si no existe
table_check = c.execute("""
SELECT name FROM sqlite_master WHERE type='table' AND name='agrupadores';
""")
if not table_check.fetchone():
    c.execute("""
    CREATE TABLE agrupadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    )
    """)
    print("✅ Tabla 'agrupadores' creada correctamente.")
else:
    print("ℹ️ La tabla 'agrupadores' ya existe.")

# Agregar columna agrupador_id a instituciones si no existe
columns = c.execute("PRAGMA table_info(instituciones)").fetchall()
col_names = [col[1] for col in columns]
if 'agrupador_id' not in col_names:
    c.execute("ALTER TABLE instituciones ADD COLUMN agrupador_id INTEGER;")
    print("✅ Columna 'agrupador_id' agregada a 'instituciones'.")
else:
    print("ℹ️ La columna 'agrupador_id' ya existe en 'instituciones'.")

conn.commit()
conn.close()
