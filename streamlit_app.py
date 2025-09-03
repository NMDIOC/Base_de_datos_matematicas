import json

DB_FILE = "usuarios.json"
CONFIG_FILE = "config.py"

with open(DB_FILE, "r", encoding="utf-8") as f:
    usuarios_data = json.load(f)

config_content = f'''# Archivo generado automáticamente. No editar manualmente.
USUARIOS_DATA = {json.dumps(usuarios_data, indent=4, ensure_ascii=False)}
'''

with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    f.write(config_content)

print(f"Archivo {CONFIG_FILE} actualizado con los datos de {DB_FILE}.")
