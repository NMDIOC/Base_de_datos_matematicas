import streamlit as st
import json
import os
import hashlib

DATA_FILE = "usuarios.json"

# --- Funciones auxiliares ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Credenciales (se podrían mover a archivo seguro) ---
ADMIN_USER = "admin"
ADMIN_PASS_HASH = hash_password("admin")

# --- Inicializar sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Interfaz de login ---
st.title("🔐 Gestión de Usuarios y Tokens")

if not st.session_state.logged_in:
    with st.expander("Iniciar sesión como administrador"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            if username == ADMIN_USER and hash_password(password) == ADMIN_PASS_HASH:
                st.session_state.logged_in = True
                st.success("Inicio de sesión correcto ✅")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

# --- Cargar usuarios ---
usuarios = load_data()

# --- Mostrar lista de usuarios ---
st.header("👥 Lista de usuarios")

if not usuarios:
    st.info("No hay usuarios registrados todavía.")
else:
    for i, user in enumerate(usuarios):
        st.write(f"### {user['nombre']}")
        st.write(f"Tokens: {user['tokens']}")

        if st.session_state.logged_in:
            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])

            with col1:
                nuevo_nombre = st.text_input("Editar nombre", value=user['nombre'], 
                                             key=f"edit_name_{user['nombre']}_{i}")
                if st.button("Guardar cambios", key=f"save_name_{i}"):
                    usuarios[i]['nombre'] = nuevo_nombre
                    save_data(usuarios)
                    st.success("Nombre actualizado ✅")
                    st.rerun()

            with col2:
                if st.button("+1", key=f"plus_{i}"):
                    usuarios[i]["tokens"] += 1
                    save_data(usuarios)
                    st.rerun()

            with col3:
                if st.button("-1", key=f"minus_{i}"):
                    usuarios[i]["tokens"] -= 1
                    save_data(usuarios)
                    st.rerun()

            with col4:
                if st.button("Eliminar", key=f"delete_{i}"):
                    usuarios.pop(i)
                    save_data(usuarios)
                    st.warning("Usuario eliminado")
                    st.rerun()

# --- Acciones de administrador ---
if st.session_state.logged_in:
    st.header("⚙️ Acciones de administrador")
    nuevo_usuario = st.text_input("Nombre nuevo usuario")
    if st.button("Añadir usuario"):
        if nuevo_usuario.strip() != "":
            usuarios.append({"nombre": nuevo_usuario, "tokens": 0})
            save_data(usuarios)
            st.success("Usuario añadido ✅")
            st.rerun()
        else:
            st.error("El nombre no puede estar vacío.")

    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.rerun()
