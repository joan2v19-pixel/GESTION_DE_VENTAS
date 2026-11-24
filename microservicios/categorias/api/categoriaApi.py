
from fastapi import APIRouter, HTTPException, status, Depends

from microservicios.usuarios.api.usuarioApi import ObtenerUsuarioAutenticado
from microservicios.categorias.api.dtos import CategoriaRegistro
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
