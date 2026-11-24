
from fastapi import APIRouter, HTTPException, status, Depends

from microservicios.usuarios.api.usuarioApi import ObtenerUsuarioAutenticado
from microservicios.proveedores.api.dtos import ProveedorRegistro
from microservicios.proveedores.servicio import proveedorServicio


router = APIRouter(
    prefix="/api/v1/proveedores",
    tags=["Gestión de proveedores"]
)


# Registrar un proveedor
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarProveedorAPI(
    datos: ProveedorRegistro,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        proveedor = proveedorServicio.RegistrarProveedorServicio(
            datos.model_dump()
        )

        return {
            "mensaje": "PROVEEDOR REGISTRADO EXITOSAMENTE.",
            "data": proveedor,
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
            detail="NO FUE POSIBLE REGISTRAR EL PROVEEDOR."
        )
