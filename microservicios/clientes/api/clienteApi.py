
from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import EmailStr

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.clientes.api.dtos import ClienteRegistro, ClienteActualizar
from microservicios.clientes.servicio import clienteServicio


router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Gestión de clientes"]
)


# REGISTRAR UN CLIENTE
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarClienteAPI(
    datos: ClienteRegistro,
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):
    try:
        cliente = clienteServicio.RegistrarClienteServicio(datos.model_dump())

        return {
            "message": "CLIENTE REGISTRADO EXITOSAMENTE.",
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


# CONSULTAR TODOS LOS CLIENTES
@router.get("/")
def ConsultarClientesAPI(
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):
    try:
        clientes = clienteServicio.ConsultarClientesServicio()

        if not clientes:
            return {
                "message": "NO HAY CLIENTES REGISTRADOS.",
                "data": [],
                "success": True
            }

        return {
            "message": "CONSULTA DE CLIENTES EXITOSA.",
            "data": clientes,
            "success": True
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LOS CLIENTES."
        )


# BUSCAR CLIENTES POR DIFERENTES CRITERIOS
@router.get("/buscar")
def BuscarClientesAPI(
    identificacion: str | None = Query(default=None, min_length=5, max_length=20),
    nombre: str | None = Query(default=None, min_length=3, max_length=100),
    telefono: str | None = Query(default=None, min_length=7, max_length=15),
    correo: EmailStr | None = Query(default=None),
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):
    # LIMPIAR LOS CRITERIOS INGRESADOS
    identificacion = identificacion.strip() if identificacion else None
    nombre = nombre.strip() if nombre else None
    telefono = telefono.strip() if telefono else None
    correo = str(correo).strip() if correo else None

    # VERIFICAR QUE SE HAYA INGRESADO AL MENOS UN CRITERIO DE BUSQUEDA
    if not any([identificacion, nombre, telefono, correo]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DEBE INGRESAR AL MENOS UN CRITERIO DE BÚSQUEDA."
        )

    try:
        clientes = clienteServicio.BuscarClientesServicio(
            identificacion,
            nombre,
            telefono,
            correo
        )

        if not clientes:
            return {
                "message": "NO SE ENCONTRARON CLIENTES CON LOS CRITERIOS INGRESADOS.",
                "data": [],
                "success": True
            }

        return {
            "message": "BÚSQUEDA DE CLIENTES EXITOSA.",
            "data": clientes,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE COMPLETAR LA BÚSQUEDA DE CLIENTES."
        )


# CONSULTAR UN CLIENTE POR ID
@router.get("/{id}")
def ObtenerClientePorIdAPI(
    id: int,
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):
    try:
        cliente = clienteServicio.ObtenerClientePorIdServicio(id)

        if cliente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NO SE ENCONTRÓ EL CLIENTE SOLICITADO."
            )

        return {
            "message": "CONSULTA DEL CLIENTE EXITOSA.",
            "data": cliente,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR EL CLIENTE."
        )


# ACTUALIZAR UN CLIENTE
@router.put("/{id}", status_code=status.HTTP_200_OK)
def ActualizarClienteAPI(
    id: int,
    datos: ClienteActualizar,
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):
    try:
        cliente = clienteServicio.ActualizarClienteServicio(
            id,
            datos.model_dump()
        )

        return {
            "message": "CLIENTE ACTUALIZADO EXITOSAMENTE.",
            "data": cliente,
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
            detail="NO FUE POSIBLE COMPLETAR LA ACTUALIZACIÓN DEL CLIENTE."
        )
