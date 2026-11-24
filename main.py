from fastapi import FastAPI
from microservicios.usuarios.api.usuarioApi import router as usuarios_router
from microservicios.clientes.api.clienteApi import router as clientes_router
from microservicios.proveedores.api.proveedorApi import router as proveedorRouter


app = FastAPI(
    title="Sistema de Gestión de Ventas e Inventario",
    description="Web Services para la gestión de usuarios",
    version="1.0.0"
)

# Registrar microservicio de usuarios
app.include_router(usuarios_router)


# Registrar microservicio de clientes
app.include_router(clientes_router)

# Registrar microservicio de proveedores
app.include_router(proveedorRouter)

@app.get("/")
def inicio():
    return {
        "mensaje": "Sistema de Gestión de Ventas e Inventario",
        "estado": "Funcionando correctamente"
    }