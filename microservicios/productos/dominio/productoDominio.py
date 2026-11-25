from microservicios.categorias.servicio import categoriaServicio
from microservicios.productos.repositorio import productoRepositorio


# REGISTRAR UN NUEVO PRODUCTO VALIDANDO REGLAS DE NEGOCIO
def RegistrarProductoDominio(datos_producto: dict) -> dict:

    # VERIFICAR QUE EL CÓDIGO DEL PRODUCTO NO ESTÉ REGISTRADO PREVIAMENTE
    producto_existente = productoRepositorio.ObtenerProductoPorCodigoRepositorio(
        datos_producto["codigo"]
    )

    if producto_existente is not None:
        raise ValueError("El código del producto ya se encuentra registrado")

    # VERIFICAR QUE LA CATEGORÍA SELECCIONADA EXISTA EN EL SISTEMA
    categoria_existente = categoriaServicio.ObtenerCategoriaPorIdServicio(
        datos_producto["categoria_id"]
    )

    if categoria_existente is None:
        raise LookupError("La categoría seleccionada no existe")

    # GUARDAR EL PRODUCTO EN EL REPOSITORIO
    return productoRepositorio.RegistrarProductoRepositorio(datos_producto)


# FORMATEAR UN PRODUCTO INCLUYENDO EL NOMBRE DE SU CATEGORÍA ASOCIADA
def _FormatearProductoConCategoria(producto: dict) -> dict:
    categoria = categoriaServicio.ObtenerCategoriaPorIdServicio(
        producto["categoria_id"]
    )
    return {
        "id": producto["id"],
        "nombre": producto["nombre"],
        "codigo": producto["codigo"],
        "precio": producto["precio"],
        "categoria_id": producto["categoria_id"],
        "categoria": categoria["nombre"] if categoria is not None else None
    }


# CONSULTAR TODOS LOS PRODUCTOS REGISTRADOS
def ConsultarProductosDominio() -> list[dict]:
    productos = productoRepositorio.ConsultarProductosRepositorio()
    return [_FormatearProductoConCategoria(producto) for producto in productos]


# CONSULTAR UN PRODUCTO POR SU IDENTIFICADOR
def ObtenerProductoPorIdDominio(id: int) -> dict | None:
    producto = productoRepositorio.ObtenerProductoPorIdRepositorio(id)
    if producto is None:
        return None
    return _FormatearProductoConCategoria(producto)


# BUSCAR PRODUCTOS POR NOMBRE O CÓDIGO
def BuscarProductosDominio(
    nombre: str | None = None,
    codigo: str | None = None
) -> list[dict]:
    productos = productoRepositorio.BuscarProductosRepositorio(nombre, codigo)
    return [_FormatearProductoConCategoria(producto) for producto in productos]
