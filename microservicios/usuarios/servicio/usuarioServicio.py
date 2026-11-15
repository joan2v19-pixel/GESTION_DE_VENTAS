from microservicios.usuarios.dominio import usuarioDominio


def RegistrarUsuarioServicio(usuario: dict):
    return usuarioDominio.RegistrarUsuarioDominio(usuario)


def ActualizarUsuarioServicio(id_usuario: int, nuevos_datos: dict):
    return usuarioDominio.ActualizarUsuarioDominio(
        id_usuario,
        nuevos_datos
    )

def ConsultarUsuariosServicio():
    return usuarioDominio.ConsultarUsuariosDominio()


def IniciarSesionServicio(nombre_usuario: str, contrasena: str):
    return usuarioDominio.IniciarSesionDominio(
        nombre_usuario,
        contrasena
    )


def ValidarSesionServicio(token: str):

    return usuarioDominio.ValidarSesionDominio(token)


def CerrarSesionServicio(token: str):

    return usuarioDominio.CerrarSesionDominio(token)


def IniciarSesionServicio(nombre_usuario: str, contrasena: str):

    return usuarioDominio.IniciarSesionDominio(
        nombre_usuario,
        contrasena
    )