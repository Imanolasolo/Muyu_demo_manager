import streamlit as st
import sqlite3
import os
import hashlib
import secrets
from jose import jwt, JWTError
from datetime import datetime, timedelta

from modules import dashboard
# Importa dashboards por rol
from modules.dashboards import admin_dashboard, comercial_dashboard, soporte_dashboard

# Agregar import para inicialización de la base de datos
from db import db_setup

# Configuración JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DB_NAME = "db/muyudemo.db"

# Funciones para hash de contraseñas usando hashlib (más compatible)
def hash_password(password: str) -> str:
    """Hash a password with a random salt using SHA-256"""
    salt = secrets.token_hex(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def verify_password_sha(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    if len(hashed) < 64:
        return False
    salt = hashed[:64]
    stored_hash = hashed[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_hash

# Inicializar la base de datos si no existe
if not os.path.exists(DB_NAME):
    db_setup.create_tables()
    db_setup.seed_fases()
    db_setup.create_admin_user()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_email(conn, email: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    return cur.fetchone()

def verify_password(plain_password, hashed_password):
    """
    Verify password - supports both bcrypt (legacy) and SHA-256 (new) hashes
    """
    try:
        # Check if it's a SHA-256 hash (our new method)
        if len(hashed_password) >= 128:  # SHA-256 hash with salt is 128+ chars
            return verify_password_sha(plain_password, hashed_password)
        else:
            # For bcrypt hashes or other legacy formats, we'll need to migrate
            # For now, if it's the admin password and matches, update it
            if plain_password == "admin123" and hashed_password.startswith("$2b$"):
                # This is the admin user with bcrypt hash, let's update it
                migrate_admin_password()
                return True
            return False
    except Exception:
        return False

def migrate_admin_password():
    """Migrate admin password from bcrypt to SHA-256"""
    try:
        conn = get_db()
        cur = conn.cursor()
        new_hash = hash_password("admin123")
        cur.execute("UPDATE usuarios SET password = ? WHERE email = ?", (new_hash, "admin@muyu.com"))
        conn.commit()
        conn.close()
        st.info("Password migrated to new format successfully!")
    except Exception as e:
        st.error(f"Error migrating password: {e}")

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def login(email, password):
    conn = get_db()
    user = get_user_by_email(conn, email)
    conn.close()
    if not user:
        return None
    # Use safe password verification from auth_utils
    from auth_utils import verify_password as safe_verify_password
    if not safe_verify_password(password, user["password"]):
        return None
    token = create_access_token({"sub": user["email"], "rol": user["rol"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return token, user

def show_dashboard(user):
    conn = get_db()
    rol = user["rol"]
    if rol == "admin":
        admin_dashboard.show(st, conn, user)
    elif rol == "comercial":
        comercial_dashboard.show(st, conn, user)
    elif rol == "soporte":
        soporte_dashboard.show(st, conn, user)
    else:
        st.error("Rol no reconocido")
    conn.close()

def main():
    st.set_page_config(page_title="Muyu Demo Manager", page_icon="📊", layout="wide")
    
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.token and st.session_state.user:
        payload = decode_token(st.session_state.token)
        if payload and payload.get("sub") == st.session_state.user["email"]:
            show_dashboard(st.session_state.user)
            if st.button("Cerrar sesión"):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
            return
        else:
            st.session_state.token = None
            st.session_state.user = None

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("assets/muyu_logo_2.png", width=200)
    with col2:
        st.title("Bienvenidos a :orange[Muyu Demo platform]")

    col1, col2 = st.columns(2)
    with col1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Entrar")
        if submitted:
            result = login(email, password)
            if result:
                token, user = result
                st.session_state.token = token
                st.session_state.user = dict(user)
                st.success("¡Login exitoso!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
                st.rerun()
    with col2:
         with st.expander("Instrucciones de uso de plataforma Demo", expanded=False):       
            st.write("1. Ingrese sus credenciales para acceder a la plataforma.")
            st.write("2. Una vez dentro, podrá navegar por las diferentes secciones según su rol.")
            st.write("3. Si tiene problemas, contacte al administrador.")

if __name__ == "__main__":
    main()
