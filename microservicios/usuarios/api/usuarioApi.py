from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Response,
    Cookie,
    Depends
)

from typing import Annotated

from microservicios.usuarios.servicio import usuarioServicio
from microservicios.usuarios.api.dtos import (
    UsuarioRegistro,
    UsuarioActualizar,
    UsuarioLogin
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
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarUsuarioAPI(
    usuario: UsuarioRegistro,
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):

    try:
        # REGISTRAR EL NUEVO USUARIO
        nuevo_usuario = usuarioServicio.RegistrarUsuarioServicio(
            usuario.model_dump()
        )

        # DEVOLVER LA INFORMACIÓN DEL USUARIO REGISTRADO
        return {
            "message": "USUARIO REGISTRADO CORRECTAMENTE.",
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


# ENDPOINT PARA ACTUALIZAR USUARIOS
@router.put("/{id_usuario}")
def ActualizarUsuarioAPI(
    id_usuario: int,
    datos: UsuarioActualizar,
    superadministrador: dict = Depends(ObtenerSuperadministrador)
):

    try:
        # ACTUALIZAR LA INFORMACIÓN DEL USUARIO
        usuario_actualizado = usuarioServicio.ActualizarUsuarioServicio(
            id_usuario,
            datos.model_dump()
        )

        # DEVOLVER LA INFORMACIÓN ACTUALIZADA
        return {
            "message": "LA INFORMACIÓN DEL USUARIO SE ACTUALIZÓ CORRECTAMENTE.",
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


# ENDPOINT PARA CONSULTAR TODOS LOS USUARIOS
@router.get("/")
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
@router.post("/login")
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
@router.post("/logout")
def CerrarSesionAPI(
    response: Response,
    sesion: Annotated[str | None, Cookie(alias="sesion")] = None
):

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
        "message": "SESIÓN CERRADA CORRECTAMENTE.",
        "success": True
    }
