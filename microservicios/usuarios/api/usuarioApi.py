
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Response,
    Cookie,
    Depends
)

from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

from microservicios.usuarios.servicio import usuarioServicio
from microservicios.usuarios.api.dtos import (
    UsuarioRegistro,
    UsuarioActualizar,
    UsuarioLogin
)


router = APIRouter(
    prefix="/api/Usuarios",
    tags=["Gestión de usuarios"]
)

# Validar que exista una sesión activa
def ObtenerUsuarioAutenticado(
    sesion: Annotated[str | None, Cookie(alias="sesion")] = None
):

    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DEBE INICIAR SESIÓN PARA ACCEDER."
        )

    try:
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


# Endpoint para registrar usuarios
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarUsuarioAPI(usuario: UsuarioRegistro):

    try:
        nuevo_usuario = usuarioServicio.RegistrarUsuarioServicio(
            usuario.model_dump()
        )

        return {
            "mensaje": "USUARIO REGISTRADO CORRECTAMENTE.",
            "data": {
                "id": nuevo_usuario["id"],
                "nombre": nuevo_usuario["nombre"],
                "identificacion": nuevo_usuario["identificacion"],
                "nombreUsuario": nuevo_usuario["nombreUsuario"]
            },
            "success": True
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


# Endpoint para actualizar usuarios
@router.put("/{id_usuario}")
def ActualizarUsuarioAPI(
    id_usuario: int,
    datos: UsuarioActualizar,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):

    try:
        usuario_actualizado = usuarioServicio.ActualizarUsuarioServicio(
            id_usuario,
            datos.model_dump()
        )

        return {
            "mensaje": "LA INFORMACIÓN DEL USUARIO SE ACTUALIZÓ CORRECTAMENTE.",
            "usuario": {
                "id": usuario_actualizado["id"],
                "nombre": usuario_actualizado["nombre"],
                "identificacion": usuario_actualizado["identificacion"],
                "nombreUsuario": usuario_actualizado["nombreUsuario"]
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


# Endpoint para consultar todos los usuarios
@router.get("/")
def ConsultarUsuariosAPI(
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):

    try:
        usuarios = usuarioServicio.ConsultarUsuariosServicio()

        return usuarios

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LOS USUARIOS."
        )


# Endpoint para iniciar sesión
@router.post("/login")
def IniciarSesionAPI(
    datos: UsuarioLogin,
    response: Response
):

    try:
        resultado = usuarioServicio.IniciarSesionServicio(
            datos.nombreUsuario,
            datos.contrasena
        )

        # Crear cookie con el identificador de sesión
        response.set_cookie(
            key="sesion",
            value=resultado["token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=1800,
            path="/api/Usuarios"
        )

        return {
            "mensaje": "INICIO DE SESIÓN EXITOSO.",
            "success": True,
            "data": resultado["usuario"]
        }

    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LA CUENTA NO SE ENCUENTRA HABILITADA PARA ACCEDER AL SISTEMA."
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="USUARIO O CONTRASEÑA INCORRECTOS."
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE COMPLETAR LA AUTENTICACIÓN."
        )


# Endpoint para consultar el usuario autenticado
@router.get("/sesion")
def ConsultarSesionAPI(
    usuario: dict = Depends(ObtenerUsuarioAutenticado)
):

    return {
        "mensaje": "SESIÓN ACTIVA.",
        "success": True,
        "data": usuario
    }


# Endpoint para cerrar sesión
@router.post("/logout")
def CerrarSesionAPI(
    response: Response,
    sesion: Annotated[str | None, Cookie(alias="sesion")] = None
):

    if sesion:
        usuarioServicio.CerrarSesionServicio(sesion)

    response.delete_cookie(
        key="sesion",
        path="/api/Usuarios",
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {
        "mensaje": "SESIÓN CERRADA CORRECTAMENTE.",
        "success": True
    }
