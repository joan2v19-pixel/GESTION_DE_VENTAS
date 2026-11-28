from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from microservicios.usuarios.api.usuarioApi import router as usuarios_router
from microservicios.categorias.api.categoriaApi import router as categoriaRouter
from microservicios.productos.api.productoApi import router as productoRouter
from microservicios.inventario.api.inventarioApi import router as inventarioRouter
from microservicios.clientes.api.clienteApi import router as clientes_router
from microservicios.proveedores.api.proveedorApi import router as proveedorRouter
from microservicios.ventas.api.ventaApi import router as ventaRouter
from microservicios.comprobantes.api.comprobanteApi import router as comprobanteRouter

# IMPORTAR LA FUNCIÓN PARA INICIALIZAR EL SUPERADMINISTRADOR
from microservicios.usuarios.dominio.usuarioDominio import InicializarSuperadministradorDominio

# CREAR LA APLICACIÓN FASTAPI
app = FastAPI(
    title="Sistema de Gestión de Ventas e Inventario",
    description="Web Services para la gestión de usuarios, catálogo, inventario, ventas y comprobantes",
    version="1.0.0"
)


# INICIALIZAR EL SUPERADMINISTRADOR AL INICIAR LA APLICACIÓN
@app.on_event("startup")
def InicializarSistema():

    InicializarSuperadministradorDominio()


# 1. REGISTRAR MICROSERVICIO DE USUARIOS (AUTENTICACIÓN)
app.include_router(usuarios_router)

# 2. REGISTRAR MICROSERVICIO DE CATEGORÍAS
app.include_router(categoriaRouter)

# 3. REGISTRAR MICROSERVICIO DE PRODUCTOS
app.include_router(productoRouter)

# 4. REGISTRAR MICROSERVICIO DE INVENTARIO
app.include_router(inventarioRouter)

# 5. REGISTRAR MICROSERVICIO DE CLIENTES
app.include_router(clientes_router)

# 6. REGISTRAR MICROSERVICIO DE PROVEEDORES
app.include_router(proveedorRouter)

# 7. REGISTRAR MICROSERVICIO DE VENTAS
app.include_router(ventaRouter)

# 8. REGISTRAR MICROSERVICIO DE COMPROBANTES
app.include_router(comprobanteRouter)


# PLANTILLAS DE MENSAJES EN ESPAÑOL PARA ERRORES DE VALIDACIÓN ESTÁNDAR
_PLANTILLAS_ERROR_VALIDACION = {
    "missing": "El campo '{campo}' es obligatorio.",
    "int_parsing": "El campo '{campo}' debe ser un número entero válido.",
    "int_type": "El campo '{campo}' debe ser un número entero válido.",
    "float_parsing": "El campo '{campo}' debe ser un número válido.",
    "float_type": "El campo '{campo}' debe ser un número válido.",
    "bool_parsing": "El campo '{campo}' debe ser un valor booleano (true o false).",
    "bool_type": "El campo '{campo}' debe ser un valor booleano (true o false).",
    "extra_forbidden": "El campo '{campo}' no está permitido.",
}


# TRADUCIR UN ERROR INDIVIDUAL DE PYDANTIC/FASTAPI A ESPAÑOL
def _TraducirDetalleValidacion(detalle: dict) -> str:
    loc = detalle.get("loc", ())
    campo = loc[-1] if loc else "solicitud"
    tipo = detalle.get("type", "")
    ctx = detalle.get("ctx") or {}

    if tipo == "json_invalid":
        return "El formato del cuerpo JSON enviado no es válido."

    if tipo in _PLANTILLAS_ERROR_VALIDACION:
        return _PLANTILLAS_ERROR_VALIDACION[tipo].format(campo=campo)

    if tipo == "string_too_short":
        return f"El campo '{campo}' debe tener al menos {ctx.get('min_length', '')} caracteres."

    if tipo == "string_too_long":
        return f"El campo '{campo}' no puede superar {ctx.get('max_length', '')} caracteres."

    if tipo == "greater_than":
        return f"El campo '{campo}' debe ser mayor que {ctx.get('gt', 0)}."

    if tipo == "greater_than_equal":
        return f"El campo '{campo}' debe ser mayor o igual que {ctx.get('ge', 0)}."

    if tipo == "value_error":
        msg = str(detalle.get("msg", "Valor no válido."))
        return msg[len("value error, "):] if msg.lower().startswith("value error, ") else msg

    return f"El campo '{campo}' no es válido."


# CONSTRUIR UN MENSAJE ÚNICO Y LEGIBLE A PARTIR DE LA LISTA DE ERRORES
def _FormatearErrorValidacion(errores: list) -> str:
    mensajes = [_TraducirDetalleValidacion(detalle) for detalle in errores]
    return " ".join(dict.fromkeys(mensajes)) or "Los datos enviados no son válidos."


# CREAR UNA RESPUESTA JSON UNIFORME PARA ERRORES GLOBALES
def _RespuestaErrorGlobal(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "message": message,
            "data": None,
            "success": False
        }
    )


# MANEJADOR GLOBAL PARA ERRORES DE VALIDACIÓN DE ENTRADA (422)
@app.exception_handler(RequestValidationError)
async def ManejadorErrorValidacion(request: Request, exc: RequestValidationError):
    return _RespuestaErrorGlobal(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        _FormatearErrorValidacion(exc.errors())
    )


# MANEJADOR GLOBAL PARA EXCEPCIONES HTTP CONTROLADAS
@app.exception_handler(HTTPException)
async def ManejadorHttpException(request: Request, exc: HTTPException):
    return _RespuestaErrorGlobal(
        exc.status_code,
        str(exc.detail) if exc.detail else "Error en la solicitud."
    )


# MANEJADOR GLOBAL PARA ERRORES INTERNOS NO CONTROLADOS (500)
@app.exception_handler(Exception)
async def ManejadorErrorGeneral(request: Request, exc: Exception):
    return _RespuestaErrorGlobal(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Ocurrió un error interno en el servidor."
    )


# DEFINIR RUTA PRINCIPAL
@app.get("/")
def inicio():

    return {
        "message": "Sistema de Gestión de Ventas e Inventario funcionando correctamente.",
        "data": None,
        "success": True
    }
