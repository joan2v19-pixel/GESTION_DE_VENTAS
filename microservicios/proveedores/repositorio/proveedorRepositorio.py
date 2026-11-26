
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


# Consultar un proveedor por ID
def ObtenerProveedorPorIdRepositorio(id: int):
    for proveedor in proveedores:
        if proveedor["id"] == id:
            return proveedor

    return None



# Buscar proveedores por diferentes criterios
def BuscarProveedoresRepositorio(
    nombre=None,
    identificacion=None,
    telefono=None,
    correo=None
):
    resultados = []

    for proveedor in proveedores:

        if identificacion and identificacion not in proveedor["identificacion"]:
            continue

        if nombre and nombre.lower() not in proveedor["nombre"].lower():
            continue

        if telefono and telefono not in proveedor["telefono"]:
            continue

        if correo and correo.lower() not in proveedor["correo"].lower():
            continue

        resultados.append(proveedor)

    return resultados



# Actualizar un proveedor
def ActualizarProveedorRepositorio(id: int, datos_proveedor: dict):
    proveedor = ObtenerProveedorPorIdRepositorio(id)

    if proveedor is None:
        return None

    proveedor.update(datos_proveedor)

    return proveedor
