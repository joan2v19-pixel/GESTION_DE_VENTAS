
from microservicios.clientes.dominio import clienteDominio


# Registrar un cliente
def RegistrarClienteServicio(datos_cliente: dict):
    return clienteDominio.RegistrarClienteDominio(datos_cliente)
