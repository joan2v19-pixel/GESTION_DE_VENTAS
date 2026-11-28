
# Lista para almacenar los clientes en memoria
clientes = []


# Registrar un cliente
def RegistrarClienteRepositorio(datos_cliente: dict):
    nuevo_cliente = {
        "id": len(clientes) + 1,
        **datos_cliente
    }

    clientes.append(nuevo_cliente)

    return nuevo_cliente


# Consultar un cliente por identificación
def ObtenerClientePorIdentificacionRepositorio(identificacion: str):
    for cliente in clientes:
        if cliente["identificacion"] == identificacion:
            return cliente

    return None


# Consultar todos los clientes
def ConsultarClientesRepositorio():
    return clientes


# Consultar un cliente por ID
def ObtenerClientePorIdRepositorio(id: int):
    for cliente in clientes:
        if cliente["id"] == id:
            return cliente

    return None



# Buscar clientes por diferentes criterios
def BuscarClientesRepositorio(
    identificacion=None,
    nombre=None,
    telefono=None,
    correo=None
):
    resultados = []

    for cliente in clientes:

        if identificacion and identificacion not in cliente["identificacion"]:
            continue

        if nombre and nombre.lower() not in cliente["nombre"].lower():
            continue

        if telefono and telefono not in cliente["telefono"]:
            continue

        if correo and correo.lower() not in cliente["correo"].lower():
            continue

        resultados.append(cliente)

    return resultados

# Actualizar un cliente
def ActualizarClienteRepositorio(id: int, datos_cliente: dict):

    cliente = ObtenerClientePorIdRepositorio(id)

    if cliente is None:
        return None

    cliente.update(datos_cliente)

    return cliente
