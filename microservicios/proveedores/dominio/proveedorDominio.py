
from microservicios.proveedores.repositorio import proveedorRepositorio


# Registrar un proveedor
def RegistrarProveedorDominio(datos_proveedor: dict):

    proveedor_existente = proveedorRepositorio.ObtenerProveedorPorIdentificacionRepositorio(
        datos_proveedor["identificacion"]
    )

    if proveedor_existente:
        raise ValueError("EL PROVEEDOR YA SE ENCUENTRA REGISTRADO.")

    return proveedorRepositorio.RegistrarProveedorRepositorio(datos_proveedor)

# Consultar todos los proveedores
def ConsultarProveedoresDominio():
    return proveedorRepositorio.ConsultarProveedoresRepositorio()


# Consultar un proveedor por ID
def ObtenerProveedorPorIdDominio(id: int):
    return proveedorRepositorio.ObtenerProveedorPorIdRepositorio(id)