
from microservicios.proveedores.repositorio import proveedorRepositorio


# Registrar un proveedor
def RegistrarProveedorDominio(datos_proveedor: dict):

    proveedor_existente = proveedorRepositorio.ObtenerProveedorPorIdentificacionRepositorio(
        datos_proveedor["identificacion"]
    )

    if proveedor_existente:
        raise ValueError("EL PROVEEDOR YA SE ENCUENTRA REGISTRADO.")

    return proveedorRepositorio.RegistrarProveedorRepositorio(datos_proveedor)
