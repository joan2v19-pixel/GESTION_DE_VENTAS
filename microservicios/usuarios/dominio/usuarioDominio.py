from pwdlib import PasswordHash
from microservicios.usuarios.repositorio import usuarioRepositorio
from datetime import datetime, timedelta, timezone
import secrets

password_hash = PasswordHash.recommended()


def RegistrarUsuarioDominio(usuario: dict):

    # Validar identificación duplicada
    if usuarioRepositorio.ExisteIdentificacionRepositorio(
        usuario["identificacion"]
    ):
        raise ValueError("La identificación ya está registrada")

    # Validar nombre de usuario duplicado
    if usuarioRepositorio.ExisteNombreUsuarioRepositorio(
        usuario["nombreUsuario"]
    ):
        raise ValueError("El nombre de usuario ya existe")

    # Proteger contraseña
    usuario["contrasena"] = password_hash.hash(
        usuario["contrasena"]
    )
    usuario["estado"] = True
    return usuarioRepositorio.RegistrarUsuarioRepositorio(usuario)


def ActualizarUsuarioDominio(id_usuario: int, nuevos_datos: dict):

    # Verificar que el usuario exista
    usuario_actual = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(
        id_usuario
    )

    if usuario_actual is None:
        raise LookupError("No se encontró el usuario solicitado")

    # Validar identificación duplicada
    if usuarioRepositorio.ExisteIdentificacionRepositorio(
        nuevos_datos["identificacion"],
        id_usuario
    ):
        raise ValueError("La identificación ya está registrada")

    # Validar nombre de usuario duplicado
    if usuarioRepositorio.ExisteNombreUsuarioRepositorio(
        nuevos_datos["nombreUsuario"],
        id_usuario
    ):
        raise ValueError("El nombre de usuario ya existe")

    return usuarioRepositorio.ActualizarUsuarioRepositorio(
        id_usuario,
        nuevos_datos
    )

def ConsultarUsuariosDominio():

    usuarios = usuarioRepositorio.ObtenerTodosUsuariosRepositorio()

    usuarios_consultados = []

    for usuario in usuarios:
        usuarios_consultados.append({
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "identificacion": usuario["identificacion"],
            "nombreUsuario": usuario["nombreUsuario"]
        })

    return usuarios_consultados

def IniciarSesionDominio(nombre_usuario: str, contrasena: str):

    usuario = usuarioRepositorio.ObtenerUsuarioPorNombreUsuarioRepositorio(
        nombre_usuario
    )

    # Verificar que el usuario exista y la contraseña sea correcta
    if usuario is None or not password_hash.verify(
        contrasena, usuario["contrasena"]
    ):
        raise ValueError("Usuario o contraseña incorrectos")

    # Verificar que la cuenta esté activa
    if not usuario.get("estado", True):
        raise PermissionError("La cuenta se encuentra inactiva")

    # Generar identificador seguro para la sesión
    token = secrets.token_urlsafe(32)

    # Establecer expiración de 30 minutos
    fecha_expiracion = datetime.now(timezone.utc) + timedelta(minutes=30)

    # Guardar la sesión
    usuarioRepositorio.CrearSesionRepositorio(
        token,
        usuario["id"],
        fecha_expiracion
    )

    return {
        "token": token,
        "usuario": {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "nombreUsuario": usuario["nombreUsuario"]
        }
    }

def ValidarSesionDominio(token: str):

    sesion = usuarioRepositorio.ObtenerSesionRepositorio(token)

    if sesion is None:
        raise ValueError("La sesión no es válida")

    # Verificar expiración
    if datetime.now(timezone.utc) >= sesion["fecha_expiracion"]:

        usuarioRepositorio.EliminarSesionRepositorio(token)

        raise ValueError("La sesión ha expirado")

    # Consultar usuario asociado a la sesión
    usuario = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(
        sesion["id_usuario"]
    )

    if usuario is None or not usuario.get("estado", True):

        usuarioRepositorio.EliminarSesionRepositorio(token)

        raise PermissionError("La cuenta no está habilitada")

    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "nombreUsuario": usuario["nombreUsuario"]
    }


def CerrarSesionDominio(token: str):

    return usuarioRepositorio.EliminarSesionRepositorio(token)