
from fastapi import APIRouter, HTTPException, status, Depends

from microservicios.usuarios.api.usuarioApi import ObtenerUsuarioAutenticado
from microservicios.categorias.api.dtos import CategoriaRegistro, CategoriaActualizar
from microservicios.categorias.servicio import categoriaServicio


router = APIRouter(
    prefix="/api/v1/categorias",
    tags=["Gestión de categorías"]
)


# Registrar una categoría
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarCategoriaAPI(
    datos: CategoriaRegistro,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        categoria = categoriaServicio.RegistrarCategoriaServicio(
            datos.model_dump()
        )

        return {
            "mensaje": "CATEGORÍA REGISTRADA EXITOSAMENTE.",
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
@router.get("/", status_code=status.HTTP_200_OK)
def ConsultarCategoriasAPI(
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        categorias = categoriaServicio.ConsultarCategoriasServicio()

        if not categorias:
            return {
                "mensaje": "NO EXISTEN CATEGORÍAS REGISTRADAS.",
                "data": [],
                "success": True
            }

        return {
            "mensaje": "CONSULTA DE CATEGORÍAS EXITOSA.",
            "data": categorias,
            "success": True
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LAS CATEGORÍAS."
        )



# Consultar una categoría por ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
def ObtenerCategoriaPorIdAPI(
    id: int,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        categoria = categoriaServicio.ObtenerCategoriaPorIdServicio(id)

        if categoria is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NO SE ENCONTRÓ LA CATEGORÍA SOLICITADA."
            )

        return {
            "mensaje": "CONSULTA DE CATEGORÍA EXITOSA.",
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
@router.put("/{id}", status_code=status.HTTP_200_OK)
def ActualizarCategoriaAPI(
    id: int,
    datos: CategoriaActualizar,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        categoriaServicio.ActualizarCategoriaServicio(
            id,
            datos.model_dump()
        )

        return {
            "mensaje": "CATEGORÍA ACTUALIZADA CORRECTAMENTE.",
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

