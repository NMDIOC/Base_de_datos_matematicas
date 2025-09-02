import streamlit as st
import json
import os
import hashlib
import pandas as pd

DB_FILE = "usuarios.json"

# ================= Funciones para JSON ================= #
def cargar_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ================= Inicialización ================= #
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = cargar_datos()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ================= Credenciales ================= #
ADMIN_USER = "admin"
# Hash de la contraseña "admin"
ADMIN_PASS_HASH = hashlib.sha256("admin".encode()).hexdigest()

def check_login(username, password):
    return username == ADMIN_USER and hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASS_HASH

# ================= Funciones ================= #
def agregar_usuario(nombre):
    if nombre in st.session_state["usuarios"]:
        st.warning("⚠️ Ese usuario ya existe.")
    else:
        st.session_state["usuarios"][nombre] = {"tokens": 0}
        guardar_datos(st.session_state["usuarios"])
        st.success(f"✅ Usuario '{nombre}' añadido.")

def eliminar_usuario(nombre):
    if nombre in st.session_state["usuarios"]:
        del st.session_state["usuarios"][nombre]
        guardar_datos(st.session_state["usuarios"])
        st.success(f"🗑️ Usuario '{nombre}' eliminado.")

def editar_usuario(nombre_antiguo, nombre_nuevo):
    if nombre_antiguo in st.session_state["usuarios"]:
        st.session_state["usuarios"][nombre_nuevo] = st.session_state["usuarios"].pop(nombre_antiguo)
        guardar_datos(st.session_state["usuarios"])
        st.success(f"✏️ Usuario '{nombre_antiguo}' renombrado a '{nombre_nuevo}'.")

def modificar_tokens(nombre, cantidad):
    if nombre in st.session_state["usuarios"]:
        st.session_state["usuarios"][nombre]["tokens"] += cantidad
        if st.session_state["usuarios"][nombre]["tokens"] < 0:
            st.session_state["usuarios"][nombre]["tokens"] = 0  # No negativos
        guardar_datos(st.session_state["usuarios"])

# ================= Interfaz ================= #
st.set_page_config(page_title="Gestor de Usuarios y Tokens", layout="wide")
st.title("👥 Gestor de Usuarios y Tokens")

# --- Login --- #
if not st.session_state["logged_in"]:
    with st.expander("🔑 Iniciar Sesión de Administrador"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if check_login(usuario, clave):
                st.session_state["logged_in"] = True
                st.success("✅ Sesión iniciada con éxito")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

# --- Modo visitante (solo ver) --- #
if not st.session_state["logged_in"]:
    st.subheader("📋 Lista de Usuarios (solo lectura)")
    if st.session_state["usuarios"]:
        df = pd.DataFrame(
            [{"Usuario": u, "Tokens": d["tokens"]} for u, d in st.session_state["usuarios"].items()]
        )
        st.table(df)
    else:
        st.info("📭 No hay usuarios registrados aún.")
    st.stop()

# --- Modo admin (control total) --- #
st.sidebar.success(f"Conectado como: {ADMIN_USER}")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["logged_in"] = False
    st.rerun()

# --- Añadir usuario --- #
st.subheader("➕ Añadir Usuario")
col1, col2 = st.columns([3,1])
with col1:
    nuevo_usuario = st.text_input("Nombre del nuevo usuario")
with col2:
    if st.button("Añadir Usuario", use_container_width=True):
        if nuevo_usuario.strip() != "":
            agregar_usuario(nuevo_usuario)
        else:
            st.warning("⚠️ El nombre no puede estar vacío.")

st.divider()

# --- Mostrar usuarios --- #
st.subheader("📋 Lista de Usuarios (modo administrador)")
if st.session_state["usuarios"]:
    for usuario, datos in st.session_state["usuarios"].items():
        col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
        with col1:
            nuevo_nombre = st.text_input("👤 Nombre:", value=usuario, key=f"edit_{usuario}")
        with col2:
            st.metric(label="🎟️ Tokens", value=datos["tokens"])
        with col3:
            if st.button("➕", key=f"add_{usuario}"):
                modificar_tokens(usuario, 1)
                st.rerun()
        with col4:
            if st.button("➖", key=f"remove_{usuario}"):
                modificar_tokens(usuario, -1)
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"delete_{usuario}"):
                eliminar_usuario(usuario)
                st.rerun()

        # Renombrar usuario si cambió
        if nuevo_nombre != usuario and nuevo_nombre.strip() != "":
            editar_usuario(usuario, nuevo_nombre)
            st.rerun()
else:
    st.info("📭 No hay usuarios registrados aún.")
