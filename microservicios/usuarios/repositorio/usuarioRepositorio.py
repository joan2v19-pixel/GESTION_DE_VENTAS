
# LISTA DE USUARIOS ALMACENADOS EN MEMORIA
usuarios = []

# DICCIONARIO QUE ALMACENA LAS SESIONES ACTIVAS DE LOS USUARIOS
sesiones = {}


# REGISTRAR UN NUEVO USUARIO EN LA LISTA
def RegistrarUsuarioRepositorio(usuario: dict):

    # GENERAR AUTOMÁTICAMENTE EL SIGUIENTE ID DISPONIBLE
    nuevo_id = max(
        [u["id"] for u in usuarios],
        default=0
    ) + 1

    # ASIGNAR EL ID AL NUEVO USUARIO
    usuario["id"] = nuevo_id

    # AGREGAR EL USUARIO A LA LISTA
    usuarios.append(usuario)

    # DEVOLVER EL USUARIO REGISTRADO
    return usuario


# OBTENER UN USUARIO MEDIANTE SU IDENTIFICADOR
def ObtenerUsuarioPorIdRepositorio(id_usuario: int):

    # RECORRER LA LISTA DE USUARIOS
    for usuario in usuarios:

        # COMPROBAR SI EL ID COINCIDE CON EL SOLICITADO
        if usuario["id"] == id_usuario:
            return usuario

    # DEVOLVER NONE SI NO SE ENCUENTRA EL USUARIO
    return None


# OBTENER TODOS LOS USUARIOS REGISTRADOS
def ObtenerTodosUsuariosRepositorio():

    # DEVOLVER LA LISTA COMPLETA DE USUARIOS
    return usuarios


# VERIFICAR SI UNA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA
def ExisteIdentificacionRepositorio(identificacion: str, id_excluir=None):

    # RECORRER LOS USUARIOS ALMACENADOS
    for usuario in usuarios:

        # COMPROBAR SI LA IDENTIFICACIÓN EXISTE
        # Y SI EL USUARIO NO CORRESPONDE AL ID EXCLUIDO
        if (
            usuario["identificacion"] == identificacion
            and usuario["id"] != id_excluir
        ):
            return True

    # DEVOLVER FALSE SI LA IDENTIFICACIÓN NO ESTÁ REGISTRADA
    return False


# VERIFICAR SI UN NOMBRE DE USUARIO YA SE ENCUENTRA REGISTRADO
def ExisteNombreUsuarioRepositorio(nombre_usuario: str, id_excluir=None):

    # RECORRER LOS USUARIOS ALMACENADOS
    for usuario in usuarios:

        # COMPARAR LOS NOMBRES DE USUARIO SIN DIFERENCIAR MAYÚSCULAS Y MINÚSCULAS
        # Y EXCLUIR EL USUARIO INDICADO SI CORRESPONDE
        if (
            usuario["nombreUsuario"].lower() == nombre_usuario.lower()
            and usuario["id"] != id_excluir
        ):
            return True

    # DEVOLVER FALSE SI EL NOMBRE DE USUARIO NO ESTÁ REGISTRADO
    return False


# ACTUALIZAR LA INFORMACIÓN DE UN USUARIO REGISTRADO
def ActualizarUsuarioRepositorio(id_usuario: int, nuevos_datos: dict):

    # RECORRER LA LISTA DE USUARIOS
    for usuario in usuarios:

        # BUSCAR EL USUARIO MEDIANTE SU ID
        if usuario["id"] == id_usuario:

            # ACTUALIZAR LOS DATOS DEL USUARIO
            usuario.update(nuevos_datos)

            # DEVOLVER EL USUARIO ACTUALIZADO
            return usuario

    # DEVOLVER NONE SI NO SE ENCUENTRA EL USUARIO
    return None


# OBTENER UN USUARIO MEDIANTE SU NOMBRE DE USUARIO
def ObtenerUsuarioPorNombreUsuarioRepositorio(nombre_usuario: str):

    # RECORRER LOS USUARIOS ALMACENADOS
    for usuario in usuarios:

        # COMPARAR LOS NOMBRES DE USUARIO SIN DIFERENCIAR MAYÚSCULAS Y MINÚSCULAS
        if usuario["nombreUsuario"].lower() == nombre_usuario.lower():
            return usuario

    # DEVOLVER NONE SI NO SE ENCUENTRA EL USUARIO
    return None


# CREAR Y ALMACENAR UNA SESIÓN PARA UN USUARIO
def CrearSesionRepositorio(token: str, id_usuario: int, fecha_expiracion):

    # GUARDAR EL TOKEN, EL ID DEL USUARIO Y LA FECHA DE EXPIRACIÓN
    sesiones[token] = {
        "id_usuario": id_usuario,
        "fecha_expiracion": fecha_expiracion
    }

    # DEVOLVER LA SESIÓN CREADA
    return sesiones[token]


# CONSULTAR UNA SESIÓN MEDIANTE SU TOKEN
def ObtenerSesionRepositorio(token: str):

    # BUSCAR Y DEVOLVER LA SESIÓN ASOCIADA AL TOKEN
    # DEVOLVER NONE SI EL TOKEN NO EXISTE
    return sesiones.get(token)


# ELIMINAR UNA SESIÓN ACTIVA
def EliminarSesionRepositorio(token: str):

    # COMPROBAR SI EL TOKEN EXISTE EN EL DICCIONARIO
    if token in sesiones:

        # ELIMINAR LA SESIÓN
        del sesiones[token]

        # INDICAR QUE LA ELIMINACIÓN FUE EXITOSA
        return True

    # DEVOLVER FALSE SI LA SESIÓN NO EXISTE
    return False


# VERIFICAR SI YA EXISTE UN SUPERADMINISTRADOR REGISTRADO
def ExisteSuperadministradorRepositorio():

    # RECORRER LOS USUARIOS ALMACENADOS
    for usuario in usuarios:

        # COMPROBAR SI EL USUARIO TIENE EL ATRIBUTO DE SUPERADMINISTRADOR ACTIVO
        if usuario.get("esSuperadministrador") is True:
            return True

    # DEVOLVER FALSE SI NO EXISTE NINGÚN SUPERADMINISTRADOR
    return False
