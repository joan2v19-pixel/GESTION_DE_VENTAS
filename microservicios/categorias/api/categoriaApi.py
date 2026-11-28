
from fastapi import APIRouter, HTTPException, Path, status, Depends

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.categorias.api.dtos import CategoriaRegistro, CategoriaActualizar
from microservicios.categorias.servicio import categoriaServicio


router = APIRouter(
    prefix="/api/v1/categorias",
    tags=["Gestión de categorías"]
)


# Registrar una categoría
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva categoría",
    description=(
        "Permite registrar una nueva categoría de productos validando los campos "
        "obligatorios (nombre y descripción), los formatos y evitando nombres duplicados."
    ),
    responses={
        201: {
            "description": "Categoría registrada correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "CATEGORÍA REGISTRADA EXITOSAMENTE.",
                        "data": {
                            "id": 1,
                            "nombre": "Accesorios",
                            "descripcion": "Categoría para productos accesorios"
                        },
                        "success": True
                    }
                }
            }
        },
        400: {
            "description": "Datos obligatorios incompletos o con formato inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "Verifique la información ingresada."}
                }
            }
        },
        409: {
            "description": "Ya existe una categoría con el mismo nombre",
            "content": {
                "application/json": {
                    "example": {"detail": "LA CATEGORÍA YA SE ENCUENTRA REGISTRADA."}
                }
            }
        },
        500: {
            "description": "Error interno al almacenar la categoría",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE REGISTRAR LA CATEGORÍA."}
                }
            }
        }
    }
)
def RegistrarCategoriaAPI(
    datos: CategoriaRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        categoria = categoriaServicio.RegistrarCategoriaServicio(
            datos.model_dump()
        )

        return {
            "message": "CATEGORÍA REGISTRADA EXITOSAMENTE.",
            "data": categoria,
            "success": True
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE REGISTRAR LA CATEGORÍA."
        )



# Consultar todas las categorías
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar y listar categorías",
    description=(
        "Obtiene el listado de todas las categorías de productos registradas en el sistema "
        "en modo de solo lectura. Si no hay categorías registradas, retorna una lista vacía "
        "y un mensaje informativo."
    ),
    responses={
        200: {
            "description": "Consulta de categorías realizada correctamente",
            "content": {
                "application/json": {
                    "examples": {
                        "con_categorias": {
                            "summary": "Existen categorías registradas",
                            "value": {
                                "message": "CONSULTA DE CATEGORÍAS EXITOSA.",
                                "data": [
                                    {
                                        "id": 1,
                                        "nombre": "Accesorios",
                                        "descripcion": "Categoría para productos accesorios"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_categorias": {
                            "summary": "No existen categorías registradas",
                            "value": {
                                "message": "NO EXISTEN CATEGORÍAS REGISTRADAS.",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar las categorías",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR LAS CATEGORÍAS."}
                }
            }
        }
    }
)
def ConsultarCategoriasAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        categorias = categoriaServicio.ConsultarCategoriasServicio()

        if not categorias:
            return {
                "message": "NO EXISTEN CATEGORÍAS REGISTRADAS.",
                "data": [],
                "success": True
            }

        return {
            "message": "CONSULTA DE CATEGORÍAS EXITOSA.",
            "data": categorias,
            "success": True
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LAS CATEGORÍAS."
        )



# Consultar una categoría por ID
@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar categoría por ID",
    description=(
        "Obtiene la información de una categoría específica mediante su identificador "
        "único sin modificar los datos almacenados."
    ),
    responses={
        200: {
            "description": "Consulta de categoría exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "CONSULTA DE CATEGORÍA EXITOSA.",
                        "data": {
                            "id": 1,
                            "nombre": "Accesorios",
                            "descripcion": "Categoría para productos accesorios"
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Categoría no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "NO SE ENCONTRÓ LA CATEGORÍA SOLICITADA."}
                }
            }
        },
        500: {
            "description": "Error interno al consultar la categoría",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR LA CATEGORÍA."}
                }
            }
        }
    }
)
def ObtenerCategoriaPorIdAPI(
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA CATEGORÍA A CONSULTAR."),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        categoria = categoriaServicio.ObtenerCategoriaPorIdServicio(id)

        if categoria is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NO SE ENCONTRÓ LA CATEGORÍA SOLICITADA."
            )

        return {
            "message": "CONSULTA DE CATEGORÍA EXITOSA.",
            "data": categoria,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LA CATEGORÍA."
        )



# Actualizar una categoría
@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar información de una categoría",
    description=(
        "Permite modificar el nombre y la descripción de una categoría existente "
        "identificada por su ID, validando obligatoriedad, formatos y unicidad del nombre."
    ),
    responses={
        200: {
            "description": "Categoría actualizada correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "CATEGORÍA ACTUALIZADA CORRECTAMENTE.",
                        "success": True
                    }
                }
            }
        },
        400: {
            "description": "Datos obligatorios incompletos o con formato inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "Verifique los campos ingresados."}
                }
            }
        },
        404: {
            "description": "La categoría seleccionada no existe",
            "content": {
                "application/json": {
                    "example": {"detail": "LA CATEGORÍA SELECCIONADA NO EXISTE."}
                }
            }
        },
        409: {
            "description": "El nombre ya se encuentra registrado en otra categoría",
            "content": {
                "application/json": {
                    "example": {"detail": "EL NOMBRE YA SE ENCUENTRA REGISTRADO EN OTRA CATEGORÍA."}
                }
            }
        },
        500: {
            "description": "Error interno al actualizar la categoría",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE ACTUALIZAR LA CATEGORÍA."}
                }
            }
        }
    }
)
def ActualizarCategoriaAPI(
    datos: CategoriaActualizar,
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA CATEGORÍA A ACTUALIZAR."),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        categoria = categoriaServicio.ActualizarCategoriaServicio(
            id,
            datos.model_dump()
        )

        return {
            "message": "CATEGORÍA ACTUALIZADA CORRECTAMENTE.",
            "data": categoria,
            "success": True
        }

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE ACTUALIZAR LA CATEGORÍA."
        )

