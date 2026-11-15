# Lista de usuarios almacenados en memoria
usuarios = []

# Diccionario de sesiones activas
sesiones = {}


def RegistrarUsuarioRepositorio(usuario: dict):
    nuevo_id = max(
        [u["id"] for u in usuarios],
        default=0
    ) + 1

    usuario["id"] = nuevo_id
    usuarios.append(usuario)

    return usuario


def ObtenerUsuarioPorIdRepositorio(id_usuario: int):
    for usuario in usuarios:
        if usuario["id"] == id_usuario:
            return usuario

    return None


def ObtenerTodosUsuariosRepositorio():
    return usuarios


def ExisteIdentificacionRepositorio(identificacion: str, id_excluir=None):
    for usuario in usuarios:
        if (
            usuario["identificacion"] == identificacion
            and usuario["id"] != id_excluir
        ):
            return True

    return False


def ExisteNombreUsuarioRepositorio(nombre_usuario: str, id_excluir=None):
    for usuario in usuarios:
        if (
            usuario["nombreUsuario"].lower() == nombre_usuario.lower()
            and usuario["id"] != id_excluir
        ):
            return True

    return False


def ActualizarUsuarioRepositorio(id_usuario: int, nuevos_datos: dict):
    for usuario in usuarios:
        if usuario["id"] == id_usuario:
            usuario.update(nuevos_datos)
            return usuario

    return None

def ObtenerUsuarioPorNombreUsuarioRepositorio(nombre_usuario: str):
    for usuario in usuarios:
        if usuario["nombreUsuario"].lower() == nombre_usuario.lower():
            return usuario

    return None

# Crear una sesión
def CrearSesionRepositorio(token: str, id_usuario: int, fecha_expiracion):

    sesiones[token] = {
        "id_usuario": id_usuario,
        "fecha_expiracion": fecha_expiracion
    }

    return sesiones[token]


# Consultar una sesión
def ObtenerSesionRepositorio(token: str):

    return sesiones.get(token)


# Eliminar una sesión
def EliminarSesionRepositorio(token: str):

    if token in sesiones:
        del sesiones[token]

        return True

    return False