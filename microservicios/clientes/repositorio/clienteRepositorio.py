
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
