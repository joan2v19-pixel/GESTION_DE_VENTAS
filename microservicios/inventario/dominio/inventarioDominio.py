from microservicios.inventario.repositorio import inventarioRepositorio
from microservicios.productos.servicio import productoServicio


# REGISTRAR EXISTENCIAS INICIALES VALIDANDO QUE EL PRODUCTO EXISTA
def RegistrarExistenciasInicialesDominio(datos_inventario: dict) -> dict:

    # VERIFICAR QUE EL PRODUCTO SELECCIONADO EXISTA EN EL SISTEMA
    producto_existente = productoServicio.ObtenerProductoPorIdServicio(
        datos_inventario["producto_id"]
    )

    if producto_existente is None:
        raise LookupError("El producto seleccionado no existe")

    # GUARDAR LAS EXISTENCIAS INICIALES EN EL REPOSITORIO
    registro = inventarioRepositorio.RegistrarExistenciasInicialesRepositorio(
        datos_inventario
    )

    # RETORNAR LA ESTRUCTURA ESPERADA DE EXISTENCIAS INICIALES
    return {
        "producto_id": registro["producto_id"],
        "cantidad_inicial": registro["cantidad_inicial"]
    }
