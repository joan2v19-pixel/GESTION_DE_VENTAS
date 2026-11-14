from fastapi import FastAPI
from microservicios.usuarios.api.usuarioApi import router as usuarios_router

app = FastAPI(
    title="Sistema de Gestión de Ventas e Inventario",
    description="Web Services para la gestión de usuarios",
    version="1.0.0"
)

# Registrar microservicio de usuarios
app.include_router(usuarios_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Sistema de Gestión de Ventas e Inventario",
        "estado": "Funcionando correctamente"
    }