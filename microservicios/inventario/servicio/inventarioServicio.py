from microservicios.inventario.dominio import inventarioDominio


# SERVICIO PARA REGISTRAR EXISTENCIAS INICIALES DE UN PRODUCTO
def RegistrarExistenciasInicialesServicio(datos_inventario: dict) -> dict:
    return inventarioDominio.RegistrarExistenciasInicialesDominio(datos_inventario)


# SERVICIO PARA CONSULTAR LAS EXISTENCIAS DISPONIBLES DE UN PRODUCTO
def ConsultarExistenciasProductoServicio(producto_id: int) -> dict:
    return inventarioDominio.ConsultarExistenciasProductoDominio(producto_id)


# SERVICIO PARA VALIDAR LA DISPONIBILIDAD DE PRODUCTOS ANTES DE UNA VENTA
def ValidarDisponibilidadServicio(productos_solicitados: list[dict]) -> dict:
    return inventarioDominio.ValidarDisponibilidadDominio(productos_solicitados)


# SERVICIO PARA DESCONTAR EXISTENCIAS DE UNA VENTA CONFIRMADA
def DescontarExistenciasVentaServicio(
    productos_venta: list[dict],
    estado_venta: str
) -> list[dict]:
    return inventarioDominio.DescontarExistenciasVentaDominio(
        productos_venta,
        estado_venta
    )
