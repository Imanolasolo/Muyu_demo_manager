import sqlite3
import os

# Nombre de la base de datos
DB_NAME = "db/muyudemo.db"

def migrate_demos_table():
    """Migrar la tabla de demos para usar fase_id en lugar de estado"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Verificar si la columna fase_id ya existe
        c.execute("PRAGMA table_info(demos)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'fase_id' not in columns:
            print("🔧 Migrando tabla demos...")
            
            # Añadir la nueva columna fase_id
            c.execute("ALTER TABLE demos ADD COLUMN fase_id INTEGER")
            
            # Obtener las fases disponibles
            c.execute("SELECT id, nombre FROM fases ORDER BY orden")
            fases = dict(c.fetchall())
            
            # Mapear los estados antiguos a fases (usar la primera fase por defecto)
            primera_fase_id = min(fases.keys()) if fases else 1
            
            # Actualizar todas las demos existentes con la primera fase
            c.execute("UPDATE demos SET fase_id = ? WHERE fase_id IS NULL", (primera_fase_id,))
            
            # Hacer que fase_id sea NOT NULL después de la migración
            c.execute("""
                CREATE TABLE demos_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    fase_id INTEGER NOT NULL,
                    institucion_id INTEGER,
                    responsable TEXT,
                    prioridad TEXT DEFAULT 'media' CHECK(prioridad IN ('baja', 'media', 'alta')),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_limite DATE,
                    FOREIGN KEY (fase_id) REFERENCES fases(id) ON DELETE SET NULL,
                    FOREIGN KEY (institucion_id) REFERENCES instituciones(id) ON DELETE SET NULL
                )
            """)
            
            # Copiar datos a la nueva tabla
            c.execute("""
                INSERT INTO demos_new (id, titulo, descripcion, fase_id, institucion_id, responsable, prioridad, fecha_creacion, fecha_actualizacion, fecha_limite)
                SELECT id, titulo, descripcion, fase_id, institucion_id, responsable, prioridad, fecha_creacion, fecha_actualizacion, fecha_limite
                FROM demos
            """)
            
            # Eliminar tabla antigua y renombrar la nueva
            c.execute("DROP TABLE demos")
            c.execute("ALTER TABLE demos_new RENAME TO demos")
            
            print("✅ Migración completada.")
        else:
            print("ℹ️ La tabla demos ya tiene la estructura correcta.")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_demos_table()
    print("✅ Migración finalizada.")