
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



# Buscar proveedores por diferentes criterios
def BuscarProveedoresDominio(
    nombre=None,
    identificacion=None,
    telefono=None,
    correo=None
):
    return proveedorRepositorio.BuscarProveedoresRepositorio(
        nombre,
        identificacion,
        telefono,
        correo
    )



# Actualizar un proveedor
def ActualizarProveedorDominio(id: int, datos_proveedor: dict):

    # Verificar que el proveedor exista
    proveedor_existente = proveedorRepositorio.ObtenerProveedorPorIdRepositorio(id)

    if proveedor_existente is None:
        raise LookupError("NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO.")

    # Verificar que la identificación no pertenezca a otro proveedor
    proveedor_identificacion = proveedorRepositorio.ObtenerProveedorPorIdentificacionRepositorio(
        datos_proveedor["identificacion"]
    )

    if proveedor_identificacion and proveedor_identificacion["id"] != id:
        raise ValueError("LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA.")

    # Actualizar el proveedor
    return proveedorRepositorio.ActualizarProveedorRepositorio(id, datos_proveedor)
