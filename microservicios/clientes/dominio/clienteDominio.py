
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
