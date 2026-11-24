
from microservicios.proveedores.dominio import proveedorDominio


# Registrar un proveedor
def RegistrarProveedorServicio(datos_proveedor: dict):
    return proveedorDominio.RegistrarProveedorDominio(datos_proveedor)


# Consultar todos los proveedores
def ConsultarProveedoresServicio():
    return proveedorDominio.ConsultarProveedoresDominio()


# Consultar un proveedor por ID
def ObtenerProveedorPorIdServicio(id: int):
    return proveedorDominio.ObtenerProveedorPorIdDominio(id)



# Buscar proveedores por diferentes criterios
def BuscarProveedoresServicio(
    nombre=None,
    identificacion=None,
    telefono=None,
    correo=None
):
    return proveedorDominio.BuscarProveedoresDominio(
        nombre,
        identificacion,
        telefono,
        correo
    )



# Actualizar un proveedor
def ActualizarProveedorServicio(id: int, datos_proveedor: dict):
    return proveedorDominio.ActualizarProveedorDominio(id, datos_proveedor)
