from fastapi import APIRouter, Body, Path, status, Depends
from fastapi.responses import JSONResponse

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.ventas.api.dtos import ConfirmarVentaSolicitud, VentaRegistro
from microservicios.ventas.servicio import ventaServicio


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE VENTAS
router = APIRouter(
    prefix="/api/v1/ventas",
    tags=["Gestión de ventas"]
)


# REGISTRAR UNA NUEVA VENTA ASOCIADA A UN CLIENTE EN ESTADO PENDIENTE
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una venta asociada a un cliente",
    description=(
        "Inicia el registro de una nueva venta en estado pendiente asociándola a un "
        "cliente previamente registrado en el sistema. Permite continuar posteriormente "
        "con el registro de productos y cantidades."
    ),
    responses={
        201: {
            "description": "Venta iniciada correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Venta iniciada correctamente",
                        "data": {
                            "venta_id": 1,
                            "cliente_id": 1,
                            "estado": "pendiente",
                            "productos": []
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "El cliente seleccionado no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El cliente seleccionado no existe",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al registrar la venta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar la venta",
                        "success": False
                    }
                }
            }
        }
    }
)
def RegistrarVentaAPI(
    datos: VentaRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        venta = ventaServicio.RegistrarVentaServicio(datos.model_dump())
        return {
            "message": "Venta iniciada correctamente",
            "data": venta,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible registrar la venta",
                "success": False
            }
        )


# CONSULTAR TODAS LAS VENTAS REGISTRADAS
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar ventas registradas",
    description="Obtiene el listado de ventas registradas con su estado y productos."
)
def ConsultarVentasAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        ventas = ventaServicio.ConsultarVentasServicio()

        if not ventas:
            return {
                "message": "No existen ventas registradas",
                "data": [],
                "success": True
            }

        return {
            "message": "Consulta de ventas exitosa",
            "data": ventas,
            "success": True
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar las ventas",
                "data": [],
                "success": False
            }
        )


# CONFIRMAR UNA VENTA Y DESCONTAR EXISTENCIAS DEL INVENTARIO
@router.post(
    "/{venta_id}/confirmar",
    status_code=status.HTTP_200_OK,
    summary="Confirmar venta y descontar existencias del inventario",
    description=(
        "Confirma una venta registrada en estado pendiente y descuenta automáticamente "
        "las cantidades vendidas del inventario. Valida que la venta exista, que no haya "
        "sido confirmada previamente, que todos los productos tengan existencias suficientes "
        "y garantiza consistencia ante errores."
    ),
    responses={
        200: {
            "description": "Venta confirmada e inventario actualizado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Venta confirmada e inventario actualizado correctamente",
                        "data": {
                            "venta_id": 1,
                            "estado": "confirmada",
                            "productos": [
                                {
                                    "producto_id": 1,
                                    "cantidad_vendida": 5,
                                    "existencias_anteriores": 100,
                                    "existencias_actuales": 95
                                },
                                {
                                    "producto_id": 2,
                                    "cantidad_vendida": 3,
                                    "existencias_anteriores": 20,
                                    "existencias_actuales": 17
                                }
                            ]
                        },
                        "success": True
                    }
                }
            }
        },
        400: {
            "description": "El identificador de la venta en el cuerpo no coincide con la ruta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El identificador de la venta en la solicitud no coincide con el de la ruta",
                        "success": False
                    }
                }
            }
        },
        404: {
            "description": "La venta seleccionada no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "La venta seleccionada no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "Existencias insuficientes o venta ya confirmada",
            "content": {
                "application/json": {
                    "examples": {
                        "existencias_insuficientes": {
                            "summary": "Inventario insuficiente",
                            "value": {
                                "message": "No hay suficiente inventario para completar la operación: producto ID 1 (solicitado: 150, disponible: 100)",
                                "success": False
                            }
                        },
                        "venta_ya_confirmada": {
                            "summary": "Venta ya confirmada previamente",
                            "value": {
                                "message": "La venta ya fue confirmada y sus existencias ya fueron descontadas",
                                "success": False
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al actualizar el inventario o confirmar la venta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible confirmar la venta y actualizar el inventario",
                        "success": False
                    }
                }
            }
        }
    }
)
def ConfirmarVentaAPI(
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    datos: ConfirmarVentaSolicitud | None = Body(default=None),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    # VALIDAR COHERENCIA SI SE ENVÍA venta_id EN EL CUERPO DE LA SOLICITUD
    if datos is not None and datos.venta_id != venta_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "El identificador de la venta en la solicitud no coincide con el de la ruta",
                "success": False
            }
        )

    try:
        # INVOCAR EL SERVICIO PARA CONFIRMAR LA VENTA Y DESCONTAR EXISTENCIAS
        resultado = ventaServicio.ConfirmarVentaServicio(venta_id)

        return {
            "message": "Venta confirmada e inventario actualizado correctamente",
            "data": resultado,
            "success": True
        }

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI LA VENTA NO EXISTE
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        # RETORNAR CONFLICTO SI FALTAN EXISTENCIAS O LA VENTA YA FUE CONFIRMADA
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA LA ACTUALIZACIÓN DEL INVENTARIO
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible confirmar la venta y actualizar el inventario",
                "success": False
            }
        )
