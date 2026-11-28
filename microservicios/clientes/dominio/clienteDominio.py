
from microservicios.clientes.repositorio import clienteRepositorio


# REGISTRAR UN CLIENTE
def RegistrarClienteDominio(datos_cliente: dict):

    # VERIFICAR SI LA IDENTIFICACIÓN YA ESTÁ REGISTRADA
    cliente_existente = clienteRepositorio.ObtenerClientePorIdentificacionRepositorio(
        datos_cliente["identificacion"]
    )

    if cliente_existente:
        raise ValueError("EL CLIENTE YA SE ENCUENTRA REGISTRADO.")

    # REGISTRAR EL CLIENTE
    return clienteRepositorio.RegistrarClienteRepositorio(datos_cliente)


# CONSULTAR TODOS LOS CLIENTES
def ConsultarClientesDominio():
    return clienteRepositorio.ConsultarClientesRepositorio()


# CONSULTAR UN CLIENTE POR ID
def ObtenerClientePorIdDominio(id: int):
    return clienteRepositorio.ObtenerClientePorIdRepositorio(id)



# BUSCAR CLIENTES POR DIFERENTES CRITERIOS
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

# ACTUALIZAR UN CLIENTE
def ActualizarClienteDominio(id: int, datos_cliente: dict):

    # VERIFICAR QUE EL CLIENTE EXISTA
    cliente_existente = clienteRepositorio.ObtenerClientePorIdRepositorio(id)

    if cliente_existente is None:
        raise LookupError("NO SE ENCONTRÓ EL CLIENTE SOLICITADO.")

    # FILTRAR CAMPOS CON VALOR POR DEFECTO 'string' PARA NO MODIFICARLOS
    datos_filtrados = {
        clave: valor
        for clave, valor in datos_cliente.items()
        if not (isinstance(valor, str) and valor.strip().lower() == "string")
    }

    # VERIFICAR QUE LA IDENTIFICACIÓN NO PERTENEZCA A OTRO CLIENTE
    if "identificacion" in datos_filtrados:
        cliente_identificacion = clienteRepositorio.ObtenerClientePorIdentificacionRepositorio(
            datos_filtrados["identificacion"]
        )

        if cliente_identificacion and cliente_identificacion["id"] != id:
            raise ValueError("LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA.")

    # ACTUALIZAR EL CLIENTE
    return clienteRepositorio.ActualizarClienteRepositorio(id, datos_filtrados)
