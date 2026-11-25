from fastapi import APIRouter, Path, status, Depends
from fastapi.responses import JSONResponse

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.productos.api.dtos import ProductoRegistro
from microservicios.productos.servicio import productoServicio


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE PRODUCTOS
router = APIRouter(
    prefix="/api/v1/productos",
    tags=["Gestión de productos"]
)


# REGISTRAR UN NUEVO PRODUCTO
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo producto",
    description=(
        "Registra un nuevo producto en el catálogo validando los campos obligatorios, "
        "que el precio sea un valor numérico mayor a cero, que el código no esté duplicado "
        "y que la categoría asociada exista en el sistema."
    ),
    responses={
        201: {
            "description": "Producto registrado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Producto registrado correctamente",
                        "data": {
                            "id": 1,
                            "nombre": "Arroz",
                            "codigo": "PROD-001",
                            "precio": 3500.0,
                            "categoria_id": 1
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "La categoría seleccionada no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "La categoría seleccionada no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "El código del producto ya se encuentra registrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El código del producto ya se encuentra registrado",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al intentar guardar el producto",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar el producto",
                        "success": False
                    }
                }
            }
        }
    }
)
def RegistrarProductoAPI(
    datos: ProductoRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # INVOCAR EL SERVICIO PARA REGISTRAR EL PRODUCTO
        producto = productoServicio.RegistrarProductoServicio(
            datos.model_dump()
        )

        # RETORNAR RESPUESTA DE REGISTRO EXITOSO
        return {
            "message": "Producto registrado correctamente",
            "data": producto,
            "success": True
        }

    except ValueError as error:
        # RETORNAR CONFLICTO SI EL CÓDIGO DEL PRODUCTO YA EXISTE
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI LA CATEGORÍA NO EXISTE
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA EL GUARDADO DEL PRODUCTO
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible registrar el producto",
                "success": False
            }
        )


# CONSULTAR TODOS LOS PRODUCTOS REGISTRADOS
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar todos los productos",
    description=(
        "Obtiene el listado completo de productos registrados en el sistema con su "
        "identificador, nombre, código, precio y categoría asociada. Si no existen "
        "registros, retorna una lista vacía."
    ),
    responses={
        200: {
            "description": "Consulta de productos exitosa o sin registros",
            "content": {
                "application/json": {
                    "examples": {
                        "con_registros": {
                            "summary": "Productos encontrados",
                            "value": {
                                "message": "Consulta de productos exitosa",
                                "data": [
                                    {
                                        "id": 1,
                                        "nombre": "Arroz",
                                        "codigo": "PROD-001",
                                        "precio": 3500.0,
                                        "categoria_id": 1,
                                        "categoria": "Granos"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_registros": {
                            "summary": "Sin productos registrados",
                            "value": {
                                "message": "No existen productos registrados",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar los productos",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible consultar los productos",
                        "data": [],
                        "success": False
                    }
                }
            }
        }
    }
)
def ConsultarProductosAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # CONSULTAR LOS PRODUCTOS DESDE EL SERVICIO
        productos = productoServicio.ConsultarProductosServicio()

        if not productos:
            return {
                "message": "No existen productos registrados",
                "data": [],
                "success": True
            }

        return {
            "message": "Consulta de productos exitosa",
            "data": productos,
            "success": True
        }

    except Exception:
        # RETORNAR ERROR CONTROLADO SI FALLA LA CONSULTA
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar los productos",
                "data": [],
                "success": False
            }
        )


# CONSULTAR UN PRODUCTO POR ID
@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar un producto por ID",
    description=(
        "Obtiene la información detallada de un producto específico (id, nombre, "
        "código, precio y categoría asociada) a partir de su identificador."
    ),
    responses={
        200: {
            "description": "Consulta de producto exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Consulta de producto exitosa",
                        "data": {
                            "id": 1,
                            "nombre": "Arroz",
                            "codigo": "PROD-001",
                            "precio": 3500.0,
                            "categoria_id": 1,
                            "categoria": "Granos"
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Producto no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No se encontró el producto solicitado",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar el producto",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible consultar el producto",
                        "success": False
                    }
                }
            }
        }
    }
)
def ObtenerProductoPorIdAPI(
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PRODUCTO"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # BUSCAR EL PRODUCTO POR SU IDENTIFICADOR
        producto = productoServicio.ObtenerProductoPorIdServicio(id)

        if producto is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "No se encontró el producto solicitado",
                    "success": False
                }
            )

        return {
            "message": "Consulta de producto exitosa",
            "data": producto,
            "success": True
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar el producto",
                "success": False
            }
        )
