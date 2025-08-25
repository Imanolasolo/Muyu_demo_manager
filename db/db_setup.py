import sqlite3
from passlib.context import CryptContext

# Nombre de la base de datos
DB_NAME = "db/muyudemo.db"

# Fases del plan demo Muyu App (según tu manual)
FASES_DEMO = [
    "Solicitud de participantes en el plan demo",
    "Activación de usuarios",
    "Coordinación reunión de onboarding",
    "Creación de grupo de WhatsApp",
    "Envío correo con pasos para descargar la app",
    "Desarrollo sesión onboarding: Muyu App y Dashboard Directivos",
    "Encuesta de satisfacción sesión de onboarding",
    "Seguimiento a usuarios participantes registrados",
    "Seguimiento a participantes para primera grabación",
    "Revisión y seguimiento dashboard",
    "Envío encuesta de percepción al equipo participante",
    "Coordinación reunión para presentación de resultados",
    "Envío propuesta comercial",
    "Seguimiento propuesta comercial"
]

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Tabla de usuarios internos (admin, comercial, soporte)
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin','comercial','soporte')),
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de instituciones educativas
    c.execute("""
    CREATE TABLE IF NOT EXISTS instituciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        responsable TEXT NOT NULL,
        email_responsable TEXT NOT NULL,
        telefono_responsable TEXT,
        estado TEXT DEFAULT 'en_progreso',
        fecha_inicio DATE DEFAULT CURRENT_DATE,
        fecha_fin DATE
    )
    """)

    # Tabla de participantes de cada institución
    c.execute("""
    CREATE TABLE IF NOT EXISTS participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institucion_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        rol TEXT CHECK(rol IN ('docente','directivo')),
        email TEXT,
        telefono TEXT,
        FOREIGN KEY (institucion_id) REFERENCES instituciones(id) ON DELETE CASCADE
    )
    """)

    # Tabla de fases generales (solo se carga una vez)
    c.execute("""
    CREATE TABLE IF NOT EXISTS fases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        orden INTEGER NOT NULL
    )
    """)

    # Tabla de seguimiento de fases por institución
    c.execute("""
    CREATE TABLE IF NOT EXISTS fases_institucion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        institucion_id INTEGER NOT NULL,
        fase_id INTEGER NOT NULL,
        estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente','en_progreso','completado')),
        responsable TEXT,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (institucion_id) REFERENCES instituciones(id) ON DELETE CASCADE,
        FOREIGN KEY (fase_id) REFERENCES fases(id)
    )
    """)

    conn.commit()
    conn.close()

def seed_fases():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Verificar si ya existen fases
    c.execute("SELECT COUNT(*) FROM fases")
    count = c.fetchone()[0]

    if count == 0:
        for i, fase in enumerate(FASES_DEMO, start=1):
            c.execute("INSERT INTO fases (nombre, descripcion, orden) VALUES (?, ?, ?)",
                      (fase, fase, i))
        print("✅ Fases cargadas correctamente.")
    else:
        print("ℹ️ Las fases ya estaban registradas.")

    conn.commit()
    conn.close()

def create_admin_user():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Cambia estos datos según tus necesidades
    admin_email = "admin@muyu.com"
    admin_nombre = "Admin"
    admin_password = "admin123"
    admin_rol = "admin"
    # Verifica si ya existe
    c.execute("SELECT * FROM usuarios WHERE email = ?", (admin_email,))
    if not c.fetchone():
        hashed = pwd_context.hash(admin_password)
        c.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
            (admin_nombre, admin_email, hashed, admin_rol)
        )
        print("✅ Usuario admin creado.")
    else:
        print("ℹ️ Usuario admin ya existe.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    seed_fases()
    create_admin_user()
    print(f"📂 Base de datos inicializada en {DB_NAME}")
