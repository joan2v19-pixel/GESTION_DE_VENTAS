
from fastapi import FastAPI
import config

# Crear aplicación FastAPI
app = FastAPI(
    title=config.APP_NAME,
    debug=config.APP_DEBUG
)

# Ruta principal
@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a Gestión de Ventas",
        "estado": "Servidor funcionando correctamente",
        "entorno": config.APP_ENV
    }

# Ruta de verificación
@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": config.APP_NAME
    }
