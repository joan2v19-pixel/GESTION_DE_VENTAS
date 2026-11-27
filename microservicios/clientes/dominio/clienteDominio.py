
from microservicios.clientes.repositorio import clienteRepositorio


# Registrar un cliente
def RegistrarClienteDominio(datos_cliente: dict):

    # Verificar si la identificación ya está registrada
    cliente_existente = clienteRepositorio.ObtenerClientePorIdentificacionRepositorio(
        datos_cliente["identificacion"]
    )

    if cliente_existente:
        raise ValueError("EL CLIENTE YA SE ENCUENTRA REGISTRADO.")

    # Registrar el cliente
    return clienteRepositorio.RegistrarClienteRepositorio(datos_cliente)


# Consultar todos los clientes
def ConsultarClientesDominio():
    return clienteRepositorio.ConsultarClientesRepositorio()


# Consultar un cliente por ID
def ObtenerClientePorIdDominio(id: int):
    return clienteRepositorio.ObtenerClientePorIdRepositorio(id)



# Buscar clientes por diferentes criterios
def BuscarClientesDominio(
    identificacion=None,
    nombre=None,
    telefono=None,
    correo=None
):
    return clienteRepositorio.BuscarClientesRepositorio(
        identificacion,
        nombre,
        telefono,
        correo
    )

# Actualizar un cliente
def ActualizarClienteDominio(id: int, datos_cliente: dict):

    # Verificar que el cliente exista
    cliente_existente = clienteRepositorio.ObtenerClientePorIdRepositorio(id)

    if cliente_existente is None:
        raise LookupError("NO SE ENCONTRÓ EL CLIENTE SOLICITADO.")

    datos_filtrados = {
        clave: valor
        for clave, valor in datos_cliente.items()
        if not (isinstance(valor, str) and valor.strip().lower() == "string")
    }

    # Verificar que la identificación no pertenezca a otro cliente
    if "identificacion" in datos_filtrados:
        cliente_identificacion = clienteRepositorio.ObtenerClientePorIdentificacionRepositorio(
            datos_filtrados["identificacion"]
        )

        if cliente_identificacion and cliente_identificacion["id"] != id:
            raise ValueError("LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA.")

    # Actualizar el cliente
    return clienteRepositorio.ActualizarClienteRepositorio(id, datos_filtrados)
