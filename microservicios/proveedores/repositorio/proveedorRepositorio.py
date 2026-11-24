
# Lista para almacenar los proveedores en memoria
proveedores = []


# Registrar un proveedor
def RegistrarProveedorRepositorio(datos_proveedor: dict):
    nuevo_proveedor = {
        "id": len(proveedores) + 1,
        **datos_proveedor
    }

    proveedores.append(nuevo_proveedor)
    return nuevo_proveedor


# Consultar un proveedor por identificación
def ObtenerProveedorPorIdentificacionRepositorio(identificacion: str):
    for proveedor in proveedores:
        if proveedor["identificacion"] == identificacion:
            return proveedor

    return None


# Consultar todos los proveedores
def ConsultarProveedoresRepositorio():
    return proveedores
