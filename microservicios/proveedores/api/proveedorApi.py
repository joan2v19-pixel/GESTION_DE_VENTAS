
import re

from fastapi import APIRouter, HTTPException, Path, Query, status, Depends

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.proveedores.api.dtos import ProveedorRegistro, ProveedorActualizar
from microservicios.proveedores.servicio import proveedorServicio


router = APIRouter(
    prefix="/api/v1/proveedores",
    tags=["Gestión de proveedores"]
)


# Registrar un proveedor
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo proveedor",
    description=(
        "Permite registrar un nuevo proveedor validando los campos obligatorios, "
        "los formatos de identificación, nombre, teléfono, correo y dirección, y "
        "verificando que la identificación no se encuentre registrada previamente."
    ),
    responses={
        201: {
            "description": "Proveedor registrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "PROVEEDOR REGISTRADO EXITOSAMENTE.",
                        "data": {
                            "id": 1,
                            "identificacion": "900123456",
                            "nombre": "Distribuidora ABC S.A.S.",
                            "telefono": "3001234567",
                            "correo": "contacto@distribuidoraabc.com",
                            "direccion": "Calle 10 # 20-30"
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
            "description": "La identificación del proveedor ya se encuentra registrada",
            "content": {
                "application/json": {
                    "example": {"detail": "EL PROVEEDOR YA SE ENCUENTRA REGISTRADO."}
                }
            }
        },
        500: {
            "description": "Error interno al almacenar el proveedor",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE REGISTRAR EL PROVEEDOR."}
                }
            }
        }
    }
)
def RegistrarProveedorAPI(
    datos: ProveedorRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        proveedor = proveedorServicio.RegistrarProveedorServicio(
            datos.model_dump()
        )

        return {
            "message": "PROVEEDOR REGISTRADO EXITOSAMENTE.",
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


# Consultar todos los proveedores
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar y listar proveedores",
    description=(
        "Obtiene el listado de todos los proveedores registrados en el sistema en modo "
        "de solo lectura. Si no hay proveedores registrados, retorna una lista vacía y "
        "un mensaje informativo."
    ),
    responses={
        200: {
            "description": "Consulta de proveedores realizada correctamente",
            "content": {
                "application/json": {
                    "examples": {
                        "con_proveedores": {
                            "summary": "Existen proveedores registrados",
                            "value": {
                                "message": "CONSULTA DE PROVEEDORES EXITOSA.",
                                "data": [
                                    {
                                        "id": 1,
                                        "identificacion": "900123456",
                                        "nombre": "Distribuidora ABC S.A.S.",
                                        "telefono": "3001234567",
                                        "correo": "contacto@distribuidoraabc.com",
                                        "direccion": "Calle 10 # 20-30"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_proveedores": {
                            "summary": "No existen proveedores registrados",
                            "value": {
                                "message": "NO EXISTEN PROVEEDORES REGISTRADOS.",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar los proveedores",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR LOS PROVEEDORES."}
                }
            }
        }
    }
)
def ConsultarProveedoresAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        proveedores = proveedorServicio.ConsultarProveedoresServicio()

        if not proveedores:
            return {
                "message": "NO EXISTEN PROVEEDORES REGISTRADOS.",
                "data": [],
                "success": True
            }

        return {
            "message": "CONSULTA DE PROVEEDORES EXITOSA.",
            "data": proveedores,
            "success": True
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LOS PROVEEDORES."
        )



# Buscar proveedores por diferentes criterios
@router.get(
    "/buscar",
    status_code=status.HTTP_200_OK,
    summary="Buscar proveedores por criterios",
    description=(
        "Permite buscar proveedores registrados utilizando uno o varios criterios "
        "(nombre, identificación, teléfono o correo electrónico) en modo de solo lectura."
    ),
    responses={
        200: {
            "description": "Búsqueda de proveedores ejecutada correctamente",
            "content": {
                "application/json": {
                    "examples": {
                        "con_resultados": {
                            "summary": "Coincidencias encontradas",
                            "value": {
                                "message": "BÚSQUEDA DE PROVEEDORES EXITOSA.",
                                "data": [
                                    {
                                        "id": 1,
                                        "identificacion": "900123456",
                                        "nombre": "Distribuidora ABC S.A.S.",
                                        "telefono": "3001234567",
                                        "correo": "contacto@distribuidoraabc.com",
                                        "direccion": "Calle 10 # 20-30"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_resultados": {
                            "summary": "Sin coincidencias",
                            "value": {
                                "message": "NO SE ENCONTRARON PROVEEDORES CON LOS CRITERIOS INGRESADOS.",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Criterios de búsqueda vacíos o con formato inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "DEBE INGRESAR AL MENOS UN CRITERIO DE BÚSQUEDA."}
                }
            }
        },
        500: {
            "description": "Error interno al realizar la búsqueda de proveedores",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE REALIZAR LA BÚSQUEDA DE PROVEEDORES."}
                }
            }
        }
    }
)
def BuscarProveedoresAPI(
    nombre: str | None = Query(
        default=None,
        min_length=3,
        max_length=100,
        description="NOMBRE O RAZÓN SOCIAL DEL PROVEEDOR."
    ),
    identificacion: str | None = Query(
        default=None,
        min_length=5,
        max_length=20,
        description="NÚMERO DE IDENTIFICACIÓN DEL PROVEEDOR (SOLO DÍGITOS)."
    ),
    telefono: str | None = Query(
        default=None,
        min_length=7,
        max_length=15,
        description="TELÉFONO DE CONTACTO DEL PROVEEDOR (SOLO DÍGITOS)."
    ),
    correo: str | None = Query(
        default=None,
        description="CORREO ELECTRÓNICO DEL PROVEEDOR."
    ),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # Limpiar los criterios ingresados
        nombre = nombre.strip() if nombre else None
        identificacion = identificacion.strip() if identificacion else None
        telefono = telefono.strip() if telefono else None
        correo = correo.strip() if correo else None

        # Validar que exista al menos un criterio
        if not any([nombre, identificacion, telefono, correo]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DEBE INGRESAR AL MENOS UN CRITERIO DE BÚSQUEDA."
            )

        # Validar formato de los criterios ingresados
        if identificacion and not identificacion.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LA IDENTIFICACIÓN SOLO DEBE CONTENER NÚMEROS."
            )

        if nombre and (
            nombre.lower() == "string"
            or not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s.,&'()\-]+", nombre)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="EL NOMBRE CONTIENE CARACTERES NO PERMITIDOS."
            )

        if telefono and not telefono.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="EL TELÉFONO SOLO DEBE CONTENER NÚMEROS."
            )

        proveedores = proveedorServicio.BuscarProveedoresServicio(
            nombre,
            identificacion,
            telefono,
            correo
        )

        if not proveedores:
            return {
                "message": "NO SE ENCONTRARON PROVEEDORES CON LOS CRITERIOS INGRESADOS.",
                "data": [],
                "success": True
            }

        return {
            "message": "BÚSQUEDA DE PROVEEDORES EXITOSA.",
            "data": proveedores,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE REALIZAR LA BÚSQUEDA DE PROVEEDORES."
        )


# Consultar un proveedor por ID
@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar proveedor por ID",
    description=(
        "Obtiene la información detallada de un proveedor registrado mediante su "
        "identificador único sin modificar los datos almacenados."
    ),
    responses={
        200: {
            "description": "Proveedor consultado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "PROVEEDOR CONSULTADO EXITOSAMENTE.",
                        "data": {
                            "id": 1,
                            "identificacion": "900123456",
                            "nombre": "Distribuidora ABC S.A.S.",
                            "telefono": "3001234567",
                            "correo": "contacto@distribuidoraabc.com",
                            "direccion": "Calle 10 # 20-30"
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Proveedor no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO."}
                }
            }
        },
        500: {
            "description": "Error interno al consultar el proveedor",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR EL PROVEEDOR."}
                }
            }
        }
    }
)
def ObtenerProveedorPorIdAPI(
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PROVEEDOR A CONSULTAR."),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        proveedor = proveedorServicio.ObtenerProveedorPorIdServicio(id)

        if proveedor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO."
            )

        return {
            "message": "PROVEEDOR CONSULTADO EXITOSAMENTE.",
            "data": proveedor,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR EL PROVEEDOR."
        )



# Actualizar un proveedor
@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar información de un proveedor",
    description=(
        "Permite modificar los datos personales, de contacto y comerciales de un "
        "proveedor existente identificado por su ID, validando formatos y evitando "
        "duplicidad de identificación."
    ),
    responses={
        200: {
            "description": "Proveedor actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "PROVEEDOR ACTUALIZADO EXITOSAMENTE.",
                        "data": {
                            "id": 1,
                            "identificacion": "900123456",
                            "nombre": "Proveedor actualizado",
                            "telefono": "3009876543",
                            "correo": "contacto@proveedor.com",
                            "direccion": "Calle 10 # 20-30"
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
            "description": "Proveedor no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO."}
                }
            }
        },
        409: {
            "description": "La identificación ya pertenece a otro proveedor",
            "content": {
                "application/json": {
                    "example": {"detail": "LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA."}
                }
            }
        },
        500: {
            "description": "Error interno al actualizar el proveedor",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE ACTUALIZAR EL PROVEEDOR."}
                }
            }
        }
    }
)
def ActualizarProveedorAPI(
    datos: ProveedorActualizar,
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PROVEEDOR A ACTUALIZAR."),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        proveedor = proveedorServicio.ActualizarProveedorServicio(
            id,
            datos.model_dump()
        )

        return {
            "message": "PROVEEDOR ACTUALIZADO EXITOSAMENTE.",
            "data": proveedor,
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
            detail="NO FUE POSIBLE ACTUALIZAR EL PROVEEDOR."
        )


