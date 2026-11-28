
from microservicios.proveedores.repositorio import proveedorRepositorio


# REGISTRAR UN PROVEEDOR
def RegistrarProveedorDominio(datos_proveedor: dict):

    # VERIFICAR SI LA IDENTIFICACIÓN YA ESTÁ REGISTRADA
    proveedor_existente = proveedorRepositorio.ObtenerProveedorPorIdentificacionRepositorio(
        datos_proveedor["identificacion"]
    )

    if proveedor_existente:
        raise ValueError("EL PROVEEDOR YA SE ENCUENTRA REGISTRADO.")

    return proveedorRepositorio.RegistrarProveedorRepositorio(datos_proveedor)

# CONSULTAR TODOS LOS PROVEEDORES
def ConsultarProveedoresDominio():
    return proveedorRepositorio.ConsultarProveedoresRepositorio()


# CONSULTAR UN PROVEEDOR POR ID
def ObtenerProveedorPorIdDominio(id: int):
    return proveedorRepositorio.ObtenerProveedorPorIdRepositorio(id)



# BUSCAR PROVEEDORES POR DIFERENTES CRITERIOS
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



# ACTUALIZAR UN PROVEEDOR
def ActualizarProveedorDominio(id: int, datos_proveedor: dict):

    # VERIFICAR QUE EL PROVEEDOR EXISTA
    proveedor_existente = proveedorRepositorio.ObtenerProveedorPorIdRepositorio(id)

    if proveedor_existente is None:
        raise LookupError("NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO.")

    # FILTRAR CAMPOS CON VALOR POR DEFECTO 'string' PARA NO MODIFICARLOS
    datos_filtrados = {
        clave: valor
        for clave, valor in datos_proveedor.items()
        if not (isinstance(valor, str) and valor.strip().lower() == "string")
    }

    # VERIFICAR QUE LA IDENTIFICACIÓN NO PERTENEZCA A OTRO PROVEEDOR
    if "identificacion" in datos_filtrados:
        proveedor_identificacion = proveedorRepositorio.ObtenerProveedorPorIdentificacionRepositorio(
            datos_filtrados["identificacion"]
        )

        if proveedor_identificacion and proveedor_identificacion["id"] != id:
            raise ValueError("LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA.")

    # ACTUALIZAR EL PROVEEDOR
    return proveedorRepositorio.ActualizarProveedorRepositorio(id, datos_filtrados)
