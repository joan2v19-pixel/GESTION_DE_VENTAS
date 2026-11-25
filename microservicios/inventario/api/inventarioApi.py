from fastapi import APIRouter, Path, status, Depends
from fastapi.responses import JSONResponse

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.inventario.api.dtos import ExistenciasInicialesRegistro
from microservicios.inventario.servicio import inventarioServicio


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE INVENTARIO
router = APIRouter(
    prefix="/api/v1/inventario",
    tags=["Gestión de inventario"]
)


# REGISTRAR EXISTENCIAS INICIALES DE UN PRODUCTO
@router.post(
    "/existencias-iniciales",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar existencias iniciales de un producto",
    description=(
        "Registra la cantidad inicial disponible de un producto previamente registrado, "
        "validando que el producto exista y que la cantidad sea un número entero mayor o igual a cero."
    ),
    responses={
        201: {
            "description": "Existencias iniciales registradas correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Existencias iniciales registradas correctamente",
                        "data": {
                            "producto_id": 1,
                            "cantidad_inicial": 100
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "El producto seleccionado no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El producto seleccionado no existe",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al guardar las existencias iniciales",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar las existencias iniciales",
                        "success": False
                    }
                }
            }
        }
    }
)
def RegistrarExistenciasInicialesAPI(
    datos: ExistenciasInicialesRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # INVOCAR EL SERVICIO PARA REGISTRAR LAS EXISTENCIAS INICIALES
        inventario = inventarioServicio.RegistrarExistenciasInicialesServicio(
            datos.model_dump()
        )

        # RETORNAR RESPUESTA DE REGISTRO EXITOSO
        return {
            "message": "Existencias iniciales registradas correctamente",
            "data": inventario,
            "success": True
        }

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI EL PRODUCTO NO EXISTE
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA EL GUARDADO DE LAS EXISTENCIAS
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible registrar las existencias iniciales",
                "success": False
            }
        )


# CONSULTAR LAS EXISTENCIAS DISPONIBLES DE UN PRODUCTO
@router.get(
    "/productos/{producto_id}/existencias",
    status_code=status.HTTP_200_OK,
    summary="Consultar existencias disponibles de un producto",
    description=(
        "Consulta la cantidad disponible en inventario de un producto registrado, "
        "validando que el producto exista. Si su cantidad disponible es cero, informa "
        "que el producto no tiene existencias disponibles."
    ),
    responses={
        200: {
            "description": "Consulta de existencias exitosa o sin existencias disponibles",
            "content": {
                "application/json": {
                    "examples": {
                        "con_existencias": {
                            "summary": "Producto con existencias disponibles",
                            "value": {
                                "message": "Consulta de existencias exitosa",
                                "data": {
                                    "producto_id": 1,
                                    "nombre_producto": "Arroz",
                                    "codigo_producto": "PROD-001",
                                    "cantidad_disponible": 100
                                },
                                "success": True
                            }
                        },
                        "sin_existencias": {
                            "summary": "Producto sin existencias disponibles",
                            "value": {
                                "message": "El producto no tiene existencias disponibles",
                                "data": {
                                    "producto_id": 1,
                                    "nombre_producto": "Arroz",
                                    "codigo_producto": "PROD-001",
                                    "cantidad_disponible": 0
                                },
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "El producto seleccionado no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El producto seleccionado no existe",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar las existencias",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible consultar las existencias del producto",
                        "success": False
                    }
                }
            }
        }
    }
)
def ConsultarExistenciasProductoAPI(
    producto_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PRODUCTO"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # CONSULTAR LAS EXISTENCIAS DEL PRODUCTO DESDE EL SERVICIO
        resultado = inventarioServicio.ConsultarExistenciasProductoServicio(producto_id)

        # INFORMAR CUANDO EL PRODUCTO NO TIENE EXISTENCIAS DISPONIBLES
        if resultado["cantidad_disponible"] == 0:
            return {
                "message": "El producto no tiene existencias disponibles",
                "data": resultado,
                "success": True
            }

        return {
            "message": "Consulta de existencias exitosa",
            "data": resultado,
            "success": True
        }

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI EL PRODUCTO NO EXISTE
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA LA CONSULTA DE EXISTENCIAS
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar las existencias del producto",
                "success": False
            }
        )
