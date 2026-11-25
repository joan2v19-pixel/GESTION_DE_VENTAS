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


# CONSULTAR TODOS LOS PRODUCTOS REGISTRADOS
def ConsultarProductosDominio() -> list[dict]:
    return productoRepositorio.ConsultarProductosRepositorio()


# CONSULTAR UN PRODUCTO POR SU IDENTIFICADOR
def ObtenerProductoPorIdDominio(id: int) -> dict | None:
    return productoRepositorio.ObtenerProductoPorIdRepositorio(id)
