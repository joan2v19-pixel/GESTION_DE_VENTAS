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


# CONSULTAR LAS EXISTENCIAS DISPONIBLES DE UN PRODUCTO REGISTRADO
def ConsultarExistenciasProductoDominio(producto_id: int) -> dict:

    # VERIFICAR QUE EL PRODUCTO EXISTA EN EL SISTEMA
    producto_existente = productoServicio.ObtenerProductoPorIdServicio(producto_id)

    if producto_existente is None:
        raise LookupError("El producto seleccionado no existe")

    # CONSULTAR LAS EXISTENCIAS DEL PRODUCTO EN EL REPOSITORIO
    inventario = inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(
        producto_id
    )

    cantidad_disponible = 0 if inventario is None else inventario["cantidad_inicial"]

    return {
        "producto_id": producto_existente["id"],
        "nombre_producto": producto_existente["nombre"],
        "codigo_producto": producto_existente["codigo"],
        "cantidad_disponible": cantidad_disponible
    }


# VALIDAR LA DISPONIBILIDAD DE MÚLTIPLES PRODUCTOS ANTES DE CONFIRMAR UNA VENTA
def ValidarDisponibilidadDominio(productos_solicitados: list[dict]) -> dict:

    detalle_productos = []

    for item in productos_solicitados:
        producto_id = item["producto_id"]
        cantidad_solicitada = item["cantidad_solicitada"]

        # VERIFICAR QUE EL PRODUCTO EXISTA EN EL SISTEMA
        producto_existente = productoServicio.ObtenerProductoPorIdServicio(producto_id)

        if producto_existente is None:
            raise LookupError(f"El producto con ID {producto_id} no existe")

        # CONSULTAR LAS EXISTENCIAS DISPONIBLES SIN MODIFICAR EL INVENTARIO
        inventario = inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(
            producto_id
        )
        cantidad_disponible = 0 if inventario is None else inventario["cantidad_inicial"]
        disponible = cantidad_disponible >= cantidad_solicitada

        detalle_productos.append({
            "producto_id": producto_id,
            "cantidad_solicitada": cantidad_solicitada,
            "cantidad_disponible": cantidad_disponible,
            "disponible": disponible
        })

    # DETERMINAR SI TODOS LOS PRODUCTOS CUENTAN CON EXISTENCIAS SUFICIENTES
    disponibilidad_suficiente = all(item["disponible"] for item in detalle_productos)

    return {
        "disponibilidad_suficiente": disponibilidad_suficiente,
        "productos": detalle_productos
    }
