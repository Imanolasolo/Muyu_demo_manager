import sqlite3
import hashlib
import secrets
import os

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


    # Tabla de agrupadores
    c.execute("""
    CREATE TABLE IF NOT EXISTS agrupadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    )
    """)

    # Tabla de instituciones educativas (ahora con agrupador_id)
    c.execute("""
    CREATE TABLE IF NOT EXISTS instituciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        responsable TEXT NOT NULL,
        email_responsable TEXT NOT NULL,
        telefono_responsable TEXT,
        estado TEXT DEFAULT 'en_progreso',
        fecha_inicio DATE DEFAULT CURRENT_DATE,
        fecha_fin DATE,
        agrupador_id INTEGER,
        FOREIGN KEY (agrupador_id) REFERENCES agrupadores(id) ON DELETE SET NULL
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

    # Tabla de fases de la demo
    c.execute("""
    CREATE TABLE IF NOT EXISTS fases_demo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        orden INTEGER NOT NULL
    )
    """)

    # Tabla de tareas asociadas a cada fase
    c.execute("""
    CREATE TABLE IF NOT EXISTS tareas_fase (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fase_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'en_progreso', 'completado')),
        FOREIGN KEY (fase_id) REFERENCES fases_demo(id) ON DELETE CASCADE
    )
    """)

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

def seed_fases_demo():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Fases de la demo
    fases = [
        {"nombre": "Inicio demo", "descripcion": "Fase inicial del demo", "orden": 1},
        {"nombre": "Onboarding", "descripcion": "Fase de onboarding", "orden": 2},
        {"nombre": "Inicio grabaciones", "descripcion": "Fase de inicio de grabaciones", "orden": 3},
        {"nombre": "Fin de grabaciones", "descripcion": "Fase de finalización de grabaciones", "orden": 4},
        {"nombre": "Resultados", "descripcion": "Fase de presentación de resultados", "orden": 5},
    ]

    # Verificar si ya existen fases
    c.execute("SELECT COUNT(*) FROM fases_demo")
    count = c.fetchone()[0]

    if count == 0:
        for fase in fases:
            c.execute("INSERT INTO fases_demo (nombre, descripcion, orden) VALUES (?, ?, ?)",
                      (fase["nombre"], fase["descripcion"], fase["orden"]))
        print("✅ Fases de demo cargadas correctamente.")
    else:
        print("ℹ️ Las fases de demo ya estaban registradas.")

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash a password with a random salt using SHA-256"""
    salt = secrets.token_hex(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def create_admin_user():
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
        hashed = hash_password(admin_password)
        c.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
            (admin_nombre, admin_email, hashed, admin_rol)
        )
        print("✅ Usuario admin creado.")
    else:
        print("ℹ️ Usuario admin ya existe.")
    conn.commit()
    conn.close()

def initialize_database():
    """Create the database file if it does not exist."""
    if not os.path.exists(DB_NAME):
        print(f"📂 Creando la base de datos en {DB_NAME}...")
        create_tables()
        seed_fases()
        seed_fases_demo()
        create_admin_user()
        print("✅ Base de datos creada e inicializada correctamente.")
    else:
        print("ℹ️ La base de datos ya existe.")

if __name__ == "__main__":
    initialize_database()
    print(f"📂 Base de datos inicializada en {DB_NAME}")
