from microservicios.inventario.dominio import inventarioDominio


# SERVICIO PARA REGISTRAR EXISTENCIAS INICIALES DE UN PRODUCTO
def RegistrarExistenciasInicialesServicio(datos_inventario: dict) -> dict:
    return inventarioDominio.RegistrarExistenciasInicialesDominio(datos_inventario)
