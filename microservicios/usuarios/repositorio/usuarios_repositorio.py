# Lista que almacenará los usuarios en memoria
usuarios = []


def obtener_todos():
    return usuarios


def obtener_por_id(id_usuario: int):
    for usuario in usuarios:
        if usuario["id"] == id_usuario:
            return usuario
    return None


def existe_identificacion(identificacion: str):
    for usuario in usuarios:
        if usuario["identificacion"] == identificacion:
            return True
    return False


def existe_nombre_usuario(nombre_usuario: str):
    for usuario in usuarios:
        if usuario["nombreUsuario"].lower() == nombre_usuario.lower():
            return True
    return False


def guardar(usuario: dict):
    usuario["id"] = len(usuarios) + 1
    usuarios.append(usuario)
    return usuario