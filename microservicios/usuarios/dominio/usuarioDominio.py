from pwdlib import PasswordHash
from microservicios.usuarios.repositorio import usuarioRepositorio

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

    if usuario is None:
        raise ValueError("Usuario o contraseña incorrectos")

    if not password_hash.verify(contrasena, usuario["contrasena"]):
        raise ValueError("Usuario o contraseña incorrectos")

    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "nombreUsuario": usuario["nombreUsuario"]
    }