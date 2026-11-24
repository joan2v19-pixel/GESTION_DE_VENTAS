from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import EmailStr
from microservicios.usuarios.api.usuarioApi import ObtenerUsuarioAutenticado

from microservicios.clientes.api.dtos import ClienteRegistro, ClienteActualizar
from microservicios.clientes.servicio import clienteServicio


router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Gestión de clientes"]
)


# Registrar un cliente
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarClienteAPI(datos: ClienteRegistro,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado) ):
    try:
        cliente = clienteServicio.RegistrarClienteServicio(datos.model_dump())

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


# Consultar todos los clientes
@router.get("/")
def ConsultarClientesAPI(usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)):
    try:
        clientes = clienteServicio.ConsultarClientesServicio()

        if not clientes:
            return {
                "mensaje": "NO HAY CLIENTES REGISTRADOS.",
                "data": [],
                "success": True
            }

        return {
            "mensaje": "CONSULTA DE CLIENTES EXITOSA.",
            "data": clientes,
            "success": True
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LOS CLIENTES."
        )


# Buscar clientes por diferentes criterios
@router.get("/buscar")
def BuscarClientesAPI(
    identificacion: str | None = Query(default=None, min_length=5, max_length=20),
    nombre: str | None = Query(default=None, min_length=3, max_length=100),
    telefono: str | None = Query(default=None, min_length=7, max_length=15),
    correo: EmailStr | None = Query(default=None),
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)

):
    # Limpiar los criterios ingresados
    identificacion = identificacion.strip() if identificacion else None
    nombre = nombre.strip() if nombre else None
    telefono = telefono.strip() if telefono else None
    correo = str(correo).strip() if correo else None

    # Verificar que se haya ingresado al menos un criterio
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
                "mensaje": "NO SE ENCONTRARON CLIENTES CON LOS CRITERIOS INGRESADOS.",
                "data": [],
                "success": True
            }

        return {
            "mensaje": "BÚSQUEDA DE CLIENTES EXITOSA.",
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


# Consultar un cliente por ID
@router.get("/{id}")
def ObtenerClientePorIdAPI(id: int,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)):
    try:
        cliente = clienteServicio.ObtenerClientePorIdServicio(id)

        if cliente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NO SE ENCONTRÓ EL CLIENTE SOLICITADO."
            )

        return {
            "mensaje": "CONSULTA DEL CLIENTE EXITOSA.",
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


# Actualizar un cliente
@router.put("/{id}", status_code=status.HTTP_200_OK)
def ActualizarClienteAPI(
    id: int,
    datos: ClienteActualizar,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        cliente = clienteServicio.ActualizarClienteServicio(
            id,
            datos.model_dump()
        )

        return {
            "mensaje": "CLIENTE ACTUALIZADO EXITOSAMENTE.",
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