
from pwdlib import PasswordHash
from microservicios.usuarios.repositorio import usuarioRepositorio
from datetime import datetime, timedelta, timezone
import secrets
import os
from dotenv import load_dotenv


# CARGAR LAS VARIABLES DE ENTORNO DEL ARCHIVO .ENV
load_dotenv()

password_hash = PasswordHash.recommended()


def RegistrarUsuarioDominio(usuario: dict):

    # VALIDAR IDENTIFICACIÓN DUPLICADA
    if usuarioRepositorio.ExisteIdentificacionRepositorio(
        usuario["identificacion"]
    ):
        raise ValueError("La identificación ya está registrada")

    # VALIDAR NOMBRE DE USUARIO DUPLICADO
    if usuarioRepositorio.ExisteNombreUsuarioRepositorio(
        usuario["nombreUsuario"]
    ):
        raise ValueError("El nombre de usuario ya existe")

    # PROTEGER CONTRASEÑA
    usuario["contrasena"] = password_hash.hash(
        usuario["contrasena"]
    )
    usuario["estado"] = True
    usuario["esSuperadministrador"] = False

    return usuarioRepositorio.RegistrarUsuarioRepositorio(usuario)


def ActualizarUsuarioDominio(id_usuario: int, nuevos_datos: dict):

    # VERIFICAR QUE EL USUARIO EXISTA
    usuario_actual = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(
        id_usuario
    )

    if usuario_actual is None:
        raise LookupError("No se encontró el usuario solicitado")

    # VALIDAR IDENTIFICACIÓN DUPLICADA
    if usuarioRepositorio.ExisteIdentificacionRepositorio(
        nuevos_datos["identificacion"],
        id_usuario
    ):
        raise ValueError("La identificación ya está registrada")

    # VALIDAR NOMBRE DE USUARIO DUPLICADO
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
            "nombreUsuario": usuario["nombreUsuario"],
            "estado": usuario.get("estado", True)
        })

    return usuarios_consultados


def IniciarSesionDominio(nombre_usuario: str, contrasena: str):

    usuario = usuarioRepositorio.ObtenerUsuarioPorNombreUsuarioRepositorio(
        nombre_usuario
    )

    # VERIFICAR QUE EL USUARIO EXISTA Y LA CONTRASEÑA SEA CORRECTA
    if usuario is None or not password_hash.verify(
        contrasena, usuario["contrasena"]
    ):
        raise ValueError("Usuario o contraseña incorrectos")

    # VERIFICAR QUE LA CUENTA ESTÉ ACTIVA
    if not usuario.get("estado", True):
        raise PermissionError("La cuenta se encuentra inactiva")

    # GENERAR IDENTIFICADOR SEGURO PARA LA SESIÓN
    token = secrets.token_urlsafe(32)

    # ESTABLECER EXPIRACIÓN DE 30 MINUTOS
    fecha_expiracion = datetime.now(timezone.utc) + timedelta(minutes=30)

    # GUARDAR LA SESIÓN
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

    # VERIFICAR EXPIRACIÓN
    if datetime.now(timezone.utc) >= sesion["fecha_expiracion"]:

        usuarioRepositorio.EliminarSesionRepositorio(token)

        raise ValueError("La sesión ha expirado")

    # CONSULTAR USUARIO ASOCIADO A LA SESIÓN
    usuario = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(
        sesion["id_usuario"]
    )

    if usuario is None or not usuario.get("estado", True):

        usuarioRepositorio.EliminarSesionRepositorio(token)

        raise PermissionError("La cuenta no está habilitada")

    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "nombreUsuario": usuario["nombreUsuario"],
        "esSuperadministrador": usuario.get("esSuperadministrador", False)
    }


def CerrarSesionDominio(token: str):

    return usuarioRepositorio.EliminarSesionRepositorio(token)


# INICIALIZAR AUTOMÁTICAMENTE EL SUPERADMINISTRADOR
def InicializarSuperadministradorDominio():

    # VERIFICAR SI YA EXISTE UN SUPERADMINISTRADOR
    if usuarioRepositorio.ExisteSuperadministradorRepositorio():
        return "EL SUPERADMINISTRADOR YA SE ENCUENTRA REGISTRADO."

    # OBTENER LOS DATOS DEL SUPERADMINISTRADOR DESDE EL ARCHIVO .ENV
    nombre = os.getenv("SUPERADMIN_NOMBRE")
    identificacion = os.getenv("SUPERADMIN_IDENTIFICACION")
    nombre_usuario = os.getenv("SUPERADMIN_USUARIO")
    contrasena = os.getenv("SUPERADMIN_CONTRASENA")

    # VALIDAR QUE TODAS LAS VARIABLES ESTÉN CONFIGURADAS
    if not all([nombre, identificacion, nombre_usuario, contrasena]):
        raise RuntimeError(
            "FALTAN VARIABLES DEL SUPERADMINISTRADOR EN EL ARCHIVO .ENV"
        )

    # VALIDAR QUE LA IDENTIFICACIÓN NO ESTÉ REGISTRADA
    if usuarioRepositorio.ExisteIdentificacionRepositorio(identificacion):
        raise RuntimeError(
            "LA IDENTIFICACIÓN CONFIGURADA PARA EL SUPERADMINISTRADOR YA EXISTE."
        )

    # VALIDAR QUE EL NOMBRE DE USUARIO NO ESTÉ REGISTRADO
    if usuarioRepositorio.ExisteNombreUsuarioRepositorio(nombre_usuario):
        raise RuntimeError(
            "EL NOMBRE DE USUARIO CONFIGURADO PARA EL SUPERADMINISTRADOR YA EXISTE."
        )

    # CREAR EL REGISTRO DEL SUPERADMINISTRADOR
    usuario = {
        "nombre": nombre,
        "identificacion": identificacion,
        "nombreUsuario": nombre_usuario,
        "contrasena": password_hash.hash(contrasena),
        "estado": True,
        "esSuperadministrador": True
    }

    # GUARDAR EL SUPERADMINISTRADOR EN EL REPOSITORIO
    usuarioRepositorio.RegistrarUsuarioRepositorio(usuario)

    return "SUPERADMINISTRADOR INICIAL REGISTRADO CORRECTAMENTE."
