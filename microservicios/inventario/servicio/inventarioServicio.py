from microservicios.inventario.dominio import inventarioDominio


# SERVICIO PARA REGISTRAR EXISTENCIAS INICIALES DE UN PRODUCTO
def RegistrarExistenciasInicialesServicio(datos_inventario: dict) -> dict:
    return inventarioDominio.RegistrarExistenciasInicialesDominio(datos_inventario)


# SERVICIO PARA CONSULTAR LAS EXISTENCIAS DISPONIBLES DE UN PRODUCTO
def ConsultarExistenciasProductoServicio(producto_id: int) -> dict:
    return inventarioDominio.ConsultarExistenciasProductoDominio(producto_id)
