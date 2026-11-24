
from microservicios.proveedores.dominio import proveedorDominio


# Registrar un proveedor
def RegistrarProveedorServicio(datos_proveedor: dict):
    return proveedorDominio.RegistrarProveedorDominio(datos_proveedor)
