import streamlit as st
import json
import os
import hashlib

# ========= Configuración ========= #
DB_FILE = "usuarios.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Usuario admin (con contraseña cifrada)
USERS = {
    "admin": hash_password("admin")
}

# ========= Funciones JSON ========= #
def cargar_usuarios():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_usuarios(usuarios):
    with open(DB_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

# ========= Inicializar estado ========= #
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = cargar_usuarios()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ========= Login ========= #
def login():
    st.subheader("🔑 Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username] == hash_password(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Bienvenido, {username}")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

def logout():
    if st.button("Cerrar Sesión"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.rerun()

# ========= Interfaz ========= #
st.title("👥 Gestión de Usuarios y Tokens")

# Mostrar lista de usuarios (igual para todos)
st.subheader("📋 Lista de Usuarios")
if len(st.session_state["usuarios"]) == 0:
    st.info("No hay usuarios registrados aún.")
else:
    for i, usuario in enumerate(st.session_state["usuarios"]):
        with st.container():
            st.write(f"**{usuario['nombre']}** — Tokens: {usuario['tokens']}")
            
            if st.session_state["logged_in"]:
                col1, col2, col3 = st.columns([1,1,1])
                with col1:
                    if st.button("➕ Token", key=f"add_token_{i}"):
                        usuario["tokens"] += 1
                        guardar_usuarios(st.session_state["usuarios"])
                        st.rerun()
                with col2:
                    if st.button("➖ Token", key=f"remove_token_{i}"):
                        if usuario["tokens"] > 0:
                            usuario["tokens"] -= 1
                            guardar_usuarios(st.session_state["usuarios"])
                            st.rerun()
                with col3:
                    if st.button("🗑️ Eliminar Usuario", key=f"delete_user_{i}"):
                        st.session_state["usuarios"].pop(i)
                        guardar_usuarios(st.session_state["usuarios"])
                        st.rerun()

st.divider()

# Opciones solo para admin
if st.session_state["logged_in"]:
    st.subheader("➕ Añadir Usuario")
    nuevo_usuario = st.text_input("Nombre del nuevo usuario")
    if st.button("Añadir"):
        if nuevo_usuario.strip():
            st.session_state["usuarios"].append({"nombre": nuevo_usuario, "tokens": 0})
            guardar_usuarios(st.session_state["usuarios"])
            st.success(f"Usuario {nuevo_usuario} añadido correctamente ✅")
            st.rerun()
        else:
            st.warning("El nombre no puede estar vacío.")

    st.divider()
    logout()
else:
    st.info("🔒 Inicia sesión como admin para gestionar usuarios y tokens.")
    login()
