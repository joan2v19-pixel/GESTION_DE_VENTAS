from microservicios.productos.dominio import productoDominio


# SERVICIO PARA REGISTRAR UN NUEVO PRODUCTO
def RegistrarProductoServicio(datos_producto: dict) -> dict:
    return productoDominio.RegistrarProductoDominio(datos_producto)


# SERVICIO PARA CONSULTAR TODOS LOS PRODUCTOS
def ConsultarProductosServicio() -> list[dict]:
    return productoDominio.ConsultarProductosDominio()


# SERVICIO PARA CONSULTAR UN PRODUCTO POR ID
def ObtenerProductoPorIdServicio(id: int) -> dict | None:
    return productoDominio.ObtenerProductoPorIdDominio(id)
