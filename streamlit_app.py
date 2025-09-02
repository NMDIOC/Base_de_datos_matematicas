import streamlit as st
import hashlib
import json
import os

# ========= Configuración ========= #
DB_FILE = "usuarios.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

USERS = {
    "admin": hash_password("admin")  # 👈 cifrado
}

# ========= Funciones de base de datos ========= #
def cargar_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_datos(datos):
    with open(DB_FILE, "w") as f:
        json.dump(datos, f, indent=4)

# ========= Estado inicial ========= #
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = cargar_datos()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ========= Login ========= #
def login():
    with st.form("login_form"):
        st.subheader("🔑 Iniciar Sesión (Admin)")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar Sesión")

        if submit:
            if username in USERS and USERS[username] == hash_password(password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"✅ Bienvenido, {username}")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

# ========= Logout ========= #
def logout():
    if st.button("Cerrar Sesión"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.rerun()

# ========= Mostrar lista de usuarios ========= #
def mostrar_usuarios():
    st.subheader("👥 Lista de Usuarios")
    if st.session_state["usuarios"]:
        for i, user in enumerate(st.session_state["usuarios"]):
            with st.container(border=True):
                st.markdown(f"**{user['nombre']}** — Tokens: {user['tokens']}")

                # Solo admin puede editar
                if st.session_state["logged_in"]:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("➕ Token", key=f"add_token_{i}"):
                            user["tokens"] += 1
                            guardar_datos(st.session_state["usuarios"])
                            st.rerun()
                    with col2:
                        if st.button("➖ Token", key=f"remove_token_{i}"):
                            user["tokens"] -= 1
                            guardar_datos(st.session_state["usuarios"])
                            st.rerun()
                    with col3:
                        nuevo_nombre = st.text_input(
                            "Editar nombre", value=user["nombre"], key=f"edit_name_{i}"
                        )
                        if nuevo_nombre != user["nombre"]:
                            user["nombre"] = nuevo_nombre
                            guardar_datos(st.session_state["usuarios"])
                    with col4:
                        if st.button("🗑️ Eliminar", key=f"delete_user_{i}"):
                            st.session_state["usuarios"].pop(i)
                            guardar_datos(st.session_state["usuarios"])
                            st.rerun()
    else:
        st.info("📭 No hay usuarios registrados")

# ========= Agregar usuario ========= #
def agregar_usuario():
    st.subheader("➕ Agregar Usuario")
    with st.form("add_user_form"):
        nombre = st.text_input("Nombre del usuario")
        tokens = st.number_input("Tokens iniciales", value=0, step=1)
        submit = st.form_submit_button("Agregar")

        if submit:
            if nombre.strip() == "":
                st.warning("⚠️ El nombre no puede estar vacío")
            else:
                st.session_state["usuarios"].append({"nombre": nombre, "tokens": int(tokens)})
                guardar_datos(st.session_state["usuarios"])
                st.success(f"✅ Usuario '{nombre}' agregado")
                st.rerun()

# ========= App ========= #
st.title("🎟️ Gestión de Usuarios y Tokens")

mostrar_usuarios()

if st.session_state["logged_in"]:
    agregar_usuario()
    logout()
else:
    st.divider()
    login()
