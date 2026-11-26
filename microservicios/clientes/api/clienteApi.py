
import re

from fastapi import APIRouter, HTTPException, Path, Query, status, Depends
from pydantic import EmailStr

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.clientes.api.dtos import ClienteRegistro, ClienteActualizar
from microservicios.clientes.servicio import clienteServicio


router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Gestión de clientes"]
)


# REGISTRAR UN CLIENTE
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo cliente",
    description=(
        "Permite registrar un nuevo cliente validando los campos obligatorios, "
        "los formatos de identificación, nombre, teléfono y correo electrónico, "
        "y verificando que la identificación no se encuentre registrada previamente."
    ),
    responses={
        201: {
            "description": "Cliente registrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "CLIENTE REGISTRADO EXITOSAMENTE.",
                        "data": {
                            "id": 1,
                            "identificacion": "1234567890",
                            "nombre": "Juan Pérez",
                            "telefono": "3001234567",
                            "correo": "juan.perez@example.com"
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
                    "example": {"detail": "Verifique los campos ingresados."}
                }
            }
        },
        409: {
            "description": "La identificación del cliente ya se encuentra registrada",
            "content": {
                "application/json": {
                    "example": {"detail": "EL CLIENTE YA SE ENCUENTRA REGISTRADO."}
                }
            }
        },
        500: {
            "description": "Error interno al almacenar el cliente",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE COMPLETAR EL REGISTRO DEL CLIENTE."}
                }
            }
        }
    }
)
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
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar y listar clientes",
    description=(
        "Obtiene el listado de todos los clientes registrados en el sistema en modo "
        "de solo lectura. Si no hay clientes registrados, retorna una lista vacía y "
        "un mensaje informativo."
    ),
    responses={
        200: {
            "description": "Consulta de clientes realizada correctamente",
            "content": {
                "application/json": {
                    "examples": {
                        "con_clientes": {
                            "summary": "Existen clientes registrados",
                            "value": {
                                "message": "CONSULTA DE CLIENTES EXITOSA.",
                                "data": [
                                    {
                                        "id": 1,
                                        "identificacion": "1234567890",
                                        "nombre": "Juan Pérez",
                                        "telefono": "3001234567",
                                        "correo": "juan.perez@example.com"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_clientes": {
                            "summary": "No existen clientes registrados",
                            "value": {
                                "message": "NO HAY CLIENTES REGISTRADOS.",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar los clientes",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR LOS CLIENTES."}
                }
            }
        }
    }
)
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
@router.get(
    "/buscar",
    status_code=status.HTTP_200_OK,
    summary="Buscar clientes por criterios",
    description=(
        "Permite buscar clientes registrados utilizando uno o varios criterios "
        "(identificación, nombre, teléfono o correo electrónico) en modo de solo lectura."
    ),
    responses={
        200: {
            "description": "Búsqueda de clientes ejecutada correctamente",
            "content": {
                "application/json": {
                    "examples": {
                        "con_resultados": {
                            "summary": "Coincidencias encontradas",
                            "value": {
                                "message": "BÚSQUEDA DE CLIENTES EXITOSA.",
                                "data": [
                                    {
                                        "id": 1,
                                        "identificacion": "1234567890",
                                        "nombre": "Juan Pérez",
                                        "telefono": "3001234567",
                                        "correo": "juan.perez@example.com"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_resultados": {
                            "summary": "Sin coincidencias",
                            "value": {
                                "message": "NO SE ENCONTRARON CLIENTES CON LOS CRITERIOS INGRESADOS.",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Criterios de búsqueda faltantes o con formato inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "DEBE INGRESAR AL MENOS UN CRITERIO DE BÚSQUEDA."}
                }
            }
        },
        500: {
            "description": "Error interno al realizar la búsqueda de clientes",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE COMPLETAR LA BÚSQUEDA DE CLIENTES."}
                }
            }
        }
    }
)
def BuscarClientesAPI(
    identificacion: str | None = Query(
        default=None,
        min_length=5,
        max_length=20,
        description="NÚMERO DE IDENTIFICACIÓN DEL CLIENTE (SOLO DÍGITOS)."
    ),
    nombre: str | None = Query(
        default=None,
        min_length=3,
        max_length=100,
        description="NOMBRE O PARTE DEL NOMBRE DEL CLIENTE (SOLO LETRAS Y ESPACIOS)."
    ),
    telefono: str | None = Query(
        default=None,
        min_length=7,
        max_length=15,
        description="TELÉFONO DE CONTACTO DEL CLIENTE (SOLO DÍGITOS)."
    ),
    correo: EmailStr | None = Query(
        default=None,
        description="CORREO ELECTRÓNICO DEL CLIENTE."
    ),
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

    # VALIDAR FORMATO DE LOS CRITERIOS INGRESADOS
    if identificacion and not identificacion.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LA IDENTIFICACIÓN SOLO DEBE CONTENER NÚMEROS."
        )

    if nombre and (
        nombre.lower() == "string"
        or not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", nombre)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS."
        )

    if telefono and not telefono.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EL TELÉFONO SOLO DEBE CONTENER NÚMEROS."
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
@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar cliente por ID",
    description=(
        "Obtiene la información detallada de un cliente registrado mediante su "
        "identificador único sin modificar los datos almacenados."
    ),
    responses={
        200: {
            "description": "Consulta del cliente exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "CONSULTA DEL CLIENTE EXITOSA.",
                        "data": {
                            "id": 1,
                            "identificacion": "1234567890",
                            "nombre": "Juan Pérez",
                            "telefono": "3001234567",
                            "correo": "juan.perez@example.com"
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Cliente no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "NO SE ENCONTRÓ EL CLIENTE SOLICITADO."}
                }
            }
        },
        500: {
            "description": "Error interno al consultar el cliente",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR EL CLIENTE."}
                }
            }
        }
    }
)
def ObtenerClientePorIdAPI(
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL CLIENTE A CONSULTAR."),
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
@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar información de un cliente",
    description=(
        "Permite modificar los datos personales y de contacto de un cliente existente "
        "identificado por su ID, validando formatos y evitando duplicidad de identificación."
    ),
    responses={
        200: {
            "description": "Cliente actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "CLIENTE ACTUALIZADO EXITOSAMENTE.",
                        "data": {
                            "id": 1,
                            "identificacion": "1234567890",
                            "nombre": "Juan Pérez Gómez",
                            "telefono": "3007654321",
                            "correo": "juan.gomez@example.com"
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
                    "example": {"detail": "Verifique los datos ingresados."}
                }
            }
        },
        404: {
            "description": "Cliente no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "NO SE ENCONTRÓ EL CLIENTE SOLICITADO."}
                }
            }
        },
        409: {
            "description": "La identificación ya pertenece a otro cliente",
            "content": {
                "application/json": {
                    "example": {"detail": "LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA."}
                }
            }
        },
        500: {
            "description": "Error interno al actualizar el cliente",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE COMPLETAR LA ACTUALIZACIÓN DEL CLIENTE."}
                }
            }
        }
    }
)
def ActualizarClienteAPI(
    datos: ClienteActualizar,
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL CLIENTE A ACTUALIZAR."),
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
