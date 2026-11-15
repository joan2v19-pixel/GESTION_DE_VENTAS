
from microservicios.clientes.dominio import clienteDominio


# Registrar un cliente
def RegistrarClienteServicio(datos_cliente: dict):
    return clienteDominio.RegistrarClienteDominio(datos_cliente)


# Consultar todos los clientes
def ConsultarClientesServicio():
    return clienteDominio.ConsultarClientesDominio()


# Consultar un cliente por ID
def ObtenerClientePorIdServicio(id: int):
    return clienteDominio.ObtenerClientePorIdDominio(id)
