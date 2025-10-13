import sqlite3
import os

# Nombre de la base de datos
DB_NAME = "db/muyudemo.db"

def actualizar_demos_con_fases():
    """Actualizar demos existentes y crear nuevas con fases correctas"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Limpiar demos existentes
        c.execute("DELETE FROM demos")
        
        # Obtener las fases disponibles
        c.execute("SELECT id, nombre FROM fases ORDER BY orden")
        fases = c.fetchall()
        
        if not fases:
            print("❌ No hay fases disponibles")
            return
        
        print(f"📋 Fases disponibles: {len(fases)}")
        for fase in fases:
            print(f"   - {fase[0]}: {fase[1]}")
        
        # Crear demos de ejemplo con diferentes fases
        demos_ejemplo = [
            {
                "titulo": "Demo Colegio San Patricio",
                "descripcion": "Implementación inicial de Muyu App para docentes de primaria",
                "fase_id": fases[0][0],  # Primera fase
                "responsable": "Admin",
                "prioridad": "alta"
            },
            {
                "titulo": "Demo Universidad Nacional", 
                "descripcion": "Piloto con profesores de ingeniería",
                "fase_id": fases[1][0] if len(fases) > 1 else fases[0][0],  # Segunda fase
                "responsable": "Admin",
                "prioridad": "media"
            },
            {
                "titulo": "Demo Instituto Tecnológico",
                "descripcion": "Evaluación de herramientas de grabación", 
                "fase_id": fases[2][0] if len(fases) > 2 else fases[0][0],  # Tercera fase
                "responsable": "Admin",
                "prioridad": "baja"
            },
            {
                "titulo": "Demo Escuela Primaria Los Andes",
                "descripcion": "Proyecto piloto con maestros de primaria",
                "fase_id": fases[0][0],  # Primera fase
                "responsable": "Admin", 
                "prioridad": "media"
            },
            {
                "titulo": "Demo Bachillerato Internacional",
                "descripcion": "Implementación para profesores de IB",
                "fase_id": fases[3][0] if len(fases) > 3 else fases[1][0],  # Cuarta fase o segunda
                "responsable": "Admin",
                "prioridad": "alta"
            }
        ]
        
        # Insertar las demos de ejemplo
        for demo in demos_ejemplo:
            c.execute("""
                INSERT INTO demos (titulo, descripcion, fase_id, responsable, prioridad)
                VALUES (?, ?, ?, ?, ?)
            """, (demo["titulo"], demo["descripcion"], demo["fase_id"], 
                  demo["responsable"], demo["prioridad"]))
        
        conn.commit()
        print(f"✅ {len(demos_ejemplo)} demos de ejemplo creadas con fases correctas.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    actualizar_demos_con_fases()
    print("✅ Actualización completada.")