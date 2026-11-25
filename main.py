
from fastapi import FastAPI

from microservicios.usuarios.api.usuarioApi import router as usuarios_router
from microservicios.clientes.api.clienteApi import router as clientes_router
from microservicios.proveedores.api.proveedorApi import router as proveedorRouter
from microservicios.categorias.api.categoriaApi import router as categoriaRouter
from microservicios.productos.api.productoApi import router as productoRouter
from microservicios.inventario.api.inventarioApi import router as inventarioRouter
from microservicios.ventas.api.ventaApi import router as ventaRouter
from microservicios.comprobantes.api.comprobanteApi import router as comprobanteRouter

# IMPORTAR LA FUNCIÓN PARA INICIALIZAR EL SUPERADMINISTRADOR
from microservicios.usuarios.dominio.usuarioDominio import InicializarSuperadministradorDominio

# CREAR LA APLICACIÓN FASTAPI
app = FastAPI(
    title="Sistema de Gestión de Ventas e Inventario",
    description="Web Services para la gestión de usuarios",
    version="1.0.0"
)


# INICIALIZAR EL SUPERADMINISTRADOR AL INICIAR LA APLICACIÓN
@app.on_event("startup")
def InicializarSistema():

    InicializarSuperadministradorDominio()


# REGISTRAR MICROSERVICIO DE USUARIOS
app.include_router(usuarios_router)


# REGISTRAR MICROSERVICIO DE CLIENTES
app.include_router(clientes_router)


# REGISTRAR MICROSERVICIO DE PROVEEDORES
app.include_router(proveedorRouter)


# REGISTRAR MICROSERVICIO DE CATEGORÍAS
app.include_router(categoriaRouter)


# REGISTRAR MICROSERVICIO DE PRODUCTOS
app.include_router(productoRouter)


# REGISTRAR MICROSERVICIO DE INVENTARIO
app.include_router(inventarioRouter)


# REGISTRAR MICROSERVICIO DE VENTAS
app.include_router(ventaRouter)


# REGISTRAR MICROSERVICIO DE COMPROBANTES
app.include_router(comprobanteRouter)


# DEFINIR RUTA PRINCIPAL
@app.get("/")
def inicio():

    return {
        "mensaje": "Sistema de Gestión de Ventas e Inventario",
        "estado": "Funcionando correctamente"
    }
