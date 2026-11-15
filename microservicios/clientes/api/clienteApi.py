
from fastapi import APIRouter, HTTPException, status

from microservicios.clientes.api.dtos import ClienteRegistro
from microservicios.clientes.servicio import clienteServicio


router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Gestión de clientes"]
)


# Registrar un cliente
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarClienteAPI(datos: ClienteRegistro):

    try:
        cliente = clienteServicio.RegistrarClienteServicio(
            datos.model_dump()
        )

        return {
            "mensaje": "CLIENTE REGISTRADO EXITOSAMENTE.",
            "data": cliente,
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
            detail="NO FUE POSIBLE COMPLETAR EL REGISTRO DEL CLIENTE."
        )
