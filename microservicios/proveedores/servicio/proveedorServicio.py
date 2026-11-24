
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