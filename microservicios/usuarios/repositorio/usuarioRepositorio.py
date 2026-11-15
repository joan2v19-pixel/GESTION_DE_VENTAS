# Lista de usuarios almacenados en memoria
usuarios = []


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