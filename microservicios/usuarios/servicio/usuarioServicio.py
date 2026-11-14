from microservicios.usuarios.dominio import usuarioDominio


def RegistrarUsuarioServicio(usuario: dict):
    return usuarioDominio.RegistrarUsuarioDominio(usuario)


def ActualizarUsuarioServicio(id_usuario: int, nuevos_datos: dict):
    return usuarioDominio.ActualizarUsuarioDominio(
        id_usuario,
        nuevos_datos
    )