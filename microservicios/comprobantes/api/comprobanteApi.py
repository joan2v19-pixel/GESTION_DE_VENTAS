from fastapi import APIRouter, Path, status, Depends
from fastapi.responses import JSONResponse

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.comprobantes.api.dtos import ComprobanteRegistro
from microservicios.comprobantes.servicio import comprobanteServicio


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE COMPROBANTES
router = APIRouter(
    prefix="/api/v1/comprobantes",
    tags=["Gestión de comprobantes"]
)


# GENERAR UN COMPROBANTE A PARTIR DE UNA VENTA CONFIRMADA
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Generar comprobante de venta",
    description=(
        "Genera y guarda un comprobante asociado a una venta previamente confirmada, "
        "incluyendo los datos del cliente, los productos vendidos, sus cantidades, "
        "subtotales y el total de la operación."
    ),
    responses={
        201: {
            "description": "Comprobante generado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Comprobante generado correctamente",
                        "data": {
                            "comprobante_id": 1,
                            "venta_id": 1,
                            "fecha_emision": "2026-11-25T15:20:00",
                            "cliente": {
                                "nombre": "Juan Pérez",
                                "identificacion": "123456789"
                            },
                            "productos": [
                                {
                                    "nombre": "Producto A",
                                    "cantidad": 2,
                                    "precio_unitario": 10000.0,
                                    "subtotal": 20000.0
                                }
                            ],
                            "total": 20000.0
                        },
                        "success": True
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
            "description": "La venta no está confirmada o faltan datos requeridos",
            "content": {
                "application/json": {
                    "examples": {
                        "venta_sin_confirmar": {
                            "summary": "Venta no confirmada",
                            "value": {
                                "message": "La venta debe estar confirmada para generar el comprobante",
                                "success": False
                            }
                        },
                        "informacion_incompleta": {
                            "summary": "Información incompleta",
                            "value": {
                                "message": "Faltan datos del cliente requeridos para generar el comprobante",
                                "success": False
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al generar o guardar el comprobante",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible generar el comprobante",
                        "success": False
                    }
                }
            }
        }
    }
)
def GenerarComprobanteAPI(
    datos: ComprobanteRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        comprobante = comprobanteServicio.GenerarComprobanteServicio(datos.venta_id)
        return {
            "message": "Comprobante generado correctamente",
            "data": comprobante,
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

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible generar el comprobante",
                "success": False
            }
        )


# CONSULTAR TODOS LOS COMPROBANTES GENERADOS
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar comprobantes generados",
    description="Obtiene el listado de todos los comprobantes generados en el sistema."
)
def ConsultarComprobantesAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        comprobantes = comprobanteServicio.ConsultarComprobantesServicio()

        if not comprobantes:
            return {
                "message": "No existen comprobantes registrados",
                "data": [],
                "success": True
            }

        return {
            "message": "Consulta de comprobantes exitosa",
            "data": comprobantes,
            "success": True
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar los comprobantes",
                "data": [],
                "success": False
            }
        )


# CONSULTAR UN COMPROBANTE POR SU IDENTIFICADOR
@router.get(
    "/{comprobante_id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar un comprobante por ID",
    description=(
        "Recupera la información de un comprobante previamente generado y verifica "
        "su asociación con una venta registrada, mostrando los datos del cliente, "
        "los productos, cantidades, subtotales y el total sin modificar los datos."
    ),
    responses={
        200: {
            "description": "Consulta del comprobante exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Consulta del comprobante exitosa",
                        "data": {
                            "comprobante_id": 1,
                            "venta_id": 1,
                            "fecha_emision": "2026-11-25T15:20:00",
                            "cliente": {
                                "nombre": "Juan Pérez",
                                "identificacion": "123456789"
                            },
                            "productos": [
                                {
                                    "nombre": "Producto A",
                                    "cantidad": 2,
                                    "precio_unitario": 10000.0,
                                    "subtotal": 20000.0
                                }
                            ],
                            "total": 20000.0
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "El comprobante solicitado no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No se encontró el comprobante solicitado",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar el comprobante",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible consultar el comprobante",
                        "success": False
                    }
                }
            }
        }
    }
)
def ObtenerComprobantePorIdAPI(
    comprobante_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL COMPROBANTE"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        comprobante = comprobanteServicio.ObtenerComprobantePorIdServicio(
            comprobante_id
        )

        if comprobante is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "No se encontró el comprobante solicitado",
                    "success": False
                }
            )

        return {
            "message": "Consulta del comprobante exitosa",
            "data": comprobante,
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
                "message": "No fue posible consultar el comprobante",
                "success": False
            }
        )
