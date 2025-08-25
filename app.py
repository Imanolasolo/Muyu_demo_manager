import streamlit as st
import sqlite3
import os
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from modules import dashboard

# Agregar import para inicialización de la base de datos
from db import db_setup

# Configuración JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DB_NAME = "db/muyudemo.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    return pwd_context.verify(plain_password, hashed_password)

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
    if not verify_password(password, user["password"]):
        return None
    token = create_access_token({"sub": user["email"], "rol": user["rol"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return token, user

def show_dashboard(user):
    conn = get_db()
    dashboard.dashboard_selector(conn)
    conn.close()

def main():
    st.set_page_config(page_title="Muyu Demo Manager", page_icon="📊")
    st.sidebar.title("Muyu Demo Manager")
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.token and st.session_state.user:
        payload = decode_token(st.session_state.token)
        if payload and payload.get("sub") == st.session_state.user["email"]:
            show_dashboard(st.session_state.user)
            if st.sidebar.button("Cerrar sesión"):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
            return
        else:
            st.session_state.token = None
            st.session_state.user = None

    st.title("Iniciar sesión")
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
            
            

if __name__ == "__main__":
    main()
