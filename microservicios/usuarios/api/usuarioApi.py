from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    status,
    Response,
    Cookie,
    Depends
)
from fastapi.responses import JSONResponse

from typing import Annotated

from microservicios.usuarios.servicio import usuarioServicio
from microservicios.usuarios.api.dtos import (
    UsuarioRegistro,
    UsuarioActualizar,
    UsuarioLogin,
    UsuarioConsulta
)


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE USUARIOS
router = APIRouter(
    prefix="/api/Usuarios",
    tags=["Gestión de usuarios"]
)


# VALIDAR QUE EXISTA UNA SESIÓN ACTIVA
def ObtenerUsuarioAutenticado(
    sesion: Annotated[
        str | None,
        Cookie(alias="sesion", include_in_schema=False)
    ] = None
):

    # VERIFICAR QUE SE HAYA ENVIADO LA COOKIE DE SESIÓN
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DEBE INICIAR SESIÓN PARA ACCEDER."
        )

    try:
        # VALIDAR LA SESIÓN Y OBTENER LOS DATOS DEL USUARIO
        return usuarioServicio.ValidarSesionServicio(sesion)

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LA CUENTA NO SE ENCUENTRA HABILITADA."
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="LA SESIÓN NO ES VÁLIDA O HA EXPIRADO."
        )


# VALIDAR QUE EL USUARIO AUTENTICADO SEA SUPERADMINISTRADOR
def ObtenerSuperadministrador(
    usuario: dict = Depends(ObtenerUsuarioAutenticado)
):

    # COMPROBAR SI EL USUARIO TIENE PERMISOS DE SUPERADMINISTRADOR
    if not usuario.get("esSuperadministrador", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="NO TIENE PERMISOS PARA REALIZAR ESTA OPERACIÓN."
        )

    # DEVOLVER LOS DATOS DEL SUPERADMINISTRADOR AUTENTICADO
    return usuario


# ENDPOINT PARA REGISTRAR USUARIOS
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description=(
        "Permite al superadministrador registrar una nueva cuenta de usuario con su "
        "información personal y credenciales de acceso, validando unicidad y protegiendo "
        "la contraseña mediante hash antes de almacenarla."
    ),
    responses={
        201: {
            "description": "Usuario registrado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Usuario registrado correctamente",
                        "data": {
                            "id": 1,
                            "nombre": "Joan Sierra",
                            "identificacion": "1234567890",
                            "nombreUsuario": "Joan"
                        },
                        "success": True
                    }
                }
            }
        },
        400: {
            "description": "Datos de entrada inválidos o incompletos",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar el usuario. Verifique los datos ingresados.",
                        "data": None,
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "Ya existe un usuario con la misma identificación o nombre de usuario",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El nombre de usuario ya existe",
                        "data": None,
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al guardar el usuario",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar el usuario",
                        "data": None,
                        "success": False
                    }
                }
            }
        }
    }
)
def RegistrarUsuarioAPI(
    usuario: UsuarioRegistro,
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):

    try:
        # REGISTRAR EL NUEVO USUARIO
        nuevo_usuario = usuarioServicio.RegistrarUsuarioServicio(
            usuario.model_dump()
        )

        # DEVOLVER LA INFORMACIÓN DEL USUARIO REGISTRADO SIN CONTRASEÑA
        return {
            "message": "Usuario registrado correctamente",
            "data": {
                "id": nuevo_usuario["id"],
                "nombre": nuevo_usuario["nombre"],
                "identificacion": nuevo_usuario["identificacion"],
                "nombreUsuario": nuevo_usuario["nombreUsuario"]
            },
            "success": True
        }

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "data": None,
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible registrar el usuario",
                "data": None,
                "success": False
            }
        )


# ENDPOINT PARA ACTUALIZAR USUARIOS
@router.put(
    "/{id_usuario}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar información de un usuario",
    description=(
        "Permite al superadministrador modificar los datos de un usuario existente "
        "identificado por su ID, incluyendo la activación o inactivación de la cuenta. "
        "Si se omite el campo estado, se conserva el valor actual. Valida formatos y "
        "unicidad sin exponer ni alterar la contraseña."
    ),
    responses={
        200: {
            "description": "Información del usuario actualizada correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "LA INFORMACIÓN DEL USUARIO SE ACTUALIZÓ CORRECTAMENTE.",
                        "usuario": {
                            "id": 1,
                            "nombre": "Laura Gomez",
                            "identificacion": "123456789",
                            "nombreUsuario": "laura.gomez",
                            "estado": True
                        },
                        "success": True
                    }
                }
            }
        },
        401: {
            "description": "No autenticado o sesión inválida/expirada",
            "content": {
                "application/json": {
                    "example": {"detail": "DEBE INICIAR SESIÓN PARA ACCEDER."}
                }
            }
        },
        403: {
            "description": "Acceso denegado: requiere permisos de superadministrador",
            "content": {
                "application/json": {
                    "example": {"detail": "NO TIENE PERMISOS PARA REALIZAR ESTA OPERACIÓN."}
                }
            }
        },
        404: {
            "description": "No se encontró el usuario solicitado",
            "content": {
                "application/json": {
                    "example": {"detail": "NO SE ENCONTRÓ EL USUARIO SOLICITADO."}
                }
            }
        },
        409: {
            "description": "Ya existe otro usuario con la misma identificación o nombre de usuario",
            "content": {
                "application/json": {
                    "example": {"detail": "El nombre de usuario ya existe"}
                }
            }
        },
        500: {
            "description": "Error interno al actualizar la información del usuario",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE ACTUALIZAR LA INFORMACIÓN DEL USUARIO."}
                }
            }
        }
    }
)
def ActualizarUsuarioAPI(
    datos: UsuarioActualizar,
    id_usuario: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL USUARIO A ACTUALIZAR."),
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):

    try:
        # ACTUALIZAR LA INFORMACIÓN DEL USUARIO
        usuario_actualizado = usuarioServicio.ActualizarUsuarioServicio(
            id_usuario,
            datos.model_dump(exclude_unset=True)
        )

        # DEVOLVER LA INFORMACIÓN ACTUALIZADA SIN CONTRASEÑA
        return {
            "message": "LA INFORMACIÓN DEL USUARIO SE ACTUALIZÓ CORRECTAMENTE.",
            "usuario": {
                "id": usuario_actualizado["id"],
                "nombre": usuario_actualizado["nombre"],
                "identificacion": usuario_actualizado["identificacion"],
                "nombreUsuario": usuario_actualizado["nombreUsuario"],
                "estado": usuario_actualizado.get("estado", True)
            },
            "success": True
        }

    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO SE ENCONTRÓ EL USUARIO SOLICITADO."
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE ACTUALIZAR LA INFORMACIÓN DEL USUARIO."
        )


# ENDPOINT PARA CONSULTAR TODOS LOS USUARIOS
@router.get(
    "/",
    response_model=list[UsuarioConsulta],
    status_code=status.HTTP_200_OK,
    summary="Consultar y listar usuarios",
    description=(
        "Permite al superadministrador consultar el listado de usuarios registrados "
        "en el sistema sin exponer contraseñas ni datos sensibles de autenticación."
    ),
    responses={
        200: {
            "description": "Listado de usuarios obtenido correctamente",
            "content": {
                "application/json": {
                    "examples": {
                        "con_usuarios": {
                            "summary": "Existen usuarios registrados",
                            "value": [
                                {
                                    "id": 1,
                                    "nombre": "Joan Sierra",
                                    "identificacion": "1234567890",
                                    "nombreUsuario": "Joan",
                                    "estado": True
                                }
                            ]
                        },
                        "sin_usuarios": {
                            "summary": "Sin usuarios registrados",
                            "value": []
                        }
                    }
                }
            }
        },
        401: {
            "description": "No autenticado o sesión inválida/expirada",
            "content": {
                "application/json": {
                    "example": {"detail": "DEBE INICIAR SESIÓN PARA ACCEDER."}
                }
            }
        },
        403: {
            "description": "Acceso denegado: requiere permisos de superadministrador",
            "content": {
                "application/json": {
                    "example": {"detail": "NO TIENE PERMISOS PARA REALIZAR ESTA OPERACIÓN."}
                }
            }
        },
        500: {
            "description": "Error interno al consultar los usuarios",
            "content": {
                "application/json": {
                    "example": {"detail": "NO FUE POSIBLE CONSULTAR LOS USUARIOS."}
                }
            }
        }
    }
)
def ConsultarUsuariosAPI(
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):

    try:
        # CONSULTAR LOS USUARIOS REGISTRADOS
        usuarios = usuarioServicio.ConsultarUsuariosServicio()

        return usuarios

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LOS USUARIOS."
        )


# ENDPOINT PARA INICIAR SESIÓN
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión en el sistema",
    description=(
        "Valida las credenciales del usuario contra el hash almacenado mediante pwdlib, "
        "verifica que la cuenta esté activa y genera una cookie de sesión HttpOnly "
        "(sesion) con vigencia de 30 minutos para acceder a las rutas protegidas."
    ),
    responses={
        200: {
            "description": "Inicio de sesión exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "message": "INICIO DE SESIÓN EXITOSO.",
                        "success": True,
                        "data": {
                            "id": 1,
                            "nombre": "Laura Gomez",
                            "nombreUsuario": "laura.gomez"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Credenciales incorrectas",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Usuario o contraseña incorrectos",
                        "success": False,
                        "data": None
                    }
                }
            }
        },
        403: {
            "description": "Cuenta inactiva o sin autorización para acceder",
            "content": {
                "application/json": {
                    "example": {
                        "message": "La cuenta no se encuentra habilitada para acceder al sistema",
                        "success": False,
                        "data": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno durante la autenticación",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible completar la autenticación",
                        "success": False,
                        "data": None
                    }
                }
            }
        }
    }
)
def IniciarSesionAPI(
    datos: UsuarioLogin,
    response: Response
):

    try:
        # VALIDAR LAS CREDENCIALES DEL USUARIO
        resultado = usuarioServicio.IniciarSesionServicio(
            datos.nombreUsuario,
            datos.contrasena
        )

        # CREAR COOKIE CON EL IDENTIFICADOR DE SESIÓN
        response.set_cookie(
            key="sesion",
            value=resultado["token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=1800,
            path="/"
        )

        return {
            "message": "INICIO DE SESIÓN EXITOSO.",
            "success": True,
            "data": resultado["usuario"]
        }

    except PermissionError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "La cuenta no se encuentra habilitada para acceder al sistema",
                "success": False,
                "data": None
            }
        )

    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "Usuario o contraseña incorrectos",
                "success": False,
                "data": None
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible completar la autenticación",
                "success": False,
                "data": None
            }
        )


# ENDPOINT PARA CONSULTAR EL USUARIO AUTENTICADO
@router.get("/sesion")
def ConsultarSesionAPI(
    usuario: dict = Depends(ObtenerUsuarioAutenticado)
):

    return {
        "mensaje": "SESIÓN ACTIVA.",
        "success": True,
        "data": usuario
    }


# ENDPOINT PARA CERRAR SESIÓN
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión en el sistema",
    description=(
        "Finaliza la sesión activa del usuario autenticado eliminando el token de sesión "
        "almacenado en el servidor y borrando la cookie HttpOnly (sesion) en el cliente. "
        "Si no existe una sesión activa, limpia la cookie de forma segura."
    ),
    responses={
        200: {
            "description": "Sesión cerrada correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Sesión cerrada correctamente",
                        "success": True
                    }
                }
            }
        },
        500: {
            "description": "Error interno al cerrar la sesión",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible cerrar la sesión",
                        "success": False
                    }
                }
            }
        }
    }
)
def CerrarSesionAPI(
    response: Response,
    sesion: Annotated[str | None, Cookie(alias="sesion")] = None
):

    try:
        # ELIMINAR LA SESIÓN SI EXISTE
        if sesion:
            usuarioServicio.CerrarSesionServicio(sesion)

        # ELIMINAR LA COOKIE DEL NAVEGADOR
        response.delete_cookie(
            key="sesion",
            path="/",
            httponly=True,
            secure=False,
            samesite="lax"
        )

        return {
            "message": "Sesión cerrada correctamente",
            "success": True
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible cerrar la sesión",
                "success": False
            }
        )
