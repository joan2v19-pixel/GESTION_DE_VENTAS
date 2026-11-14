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