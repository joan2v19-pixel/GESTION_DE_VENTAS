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


# DESCONTAR EXISTENCIAS DEL INVENTARIO PARA UNA VENTA CONFIRMADA CON REVERSIÓN ANTE ERRORES
def DescontarExistenciasVentaDominio(
    productos_venta: list[dict],
    estado_venta: str
) -> list[dict]:

    # IMPEDIR DESCUENTOS SI LA VENTA NO ESTÁ CONFIRMADA
    if estado_venta != "confirmada":
        raise ValueError("No se pueden descontar existencias de una venta no confirmada")

    # AGRUPAR CANTIDADES POR PRODUCTO PARA EVITAR INCONSISTENCIAS SI SE REPITE UN PRODUCTO
    cantidades_por_producto: dict[int, int] = {}
    for item in productos_venta:
        producto_id = item["producto_id"]
        cantidad = item["cantidad"]
        cantidades_por_producto[producto_id] = (
            cantidades_por_producto.get(producto_id, 0) + cantidad
        )

    # VALIDAR EXISTENCIA Y DISPONIBILIDAD ANTES DE REALIZAR CUALQUIER MODIFICACIÓN
    respaldo_anterior: list[tuple[int, int]] = []
    resumen_descuento: list[dict] = []

    for producto_id, cantidad_vendida in cantidades_por_producto.items():
        producto_existente = productoServicio.ObtenerProductoPorIdServicio(producto_id)
        if producto_existente is None:
            raise LookupError(f"El producto con ID {producto_id} no existe")

        inventario = inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(
            producto_id
        )
        existencias_anteriores = 0 if inventario is None else inventario["cantidad_inicial"]

        if existencias_anteriores < cantidad_vendida:
            raise ValueError(
                f"Existencias insuficientes para el producto ID {producto_id}: "
                f"solicitado {cantidad_vendida}, disponible {existencias_anteriores}"
            )

        existencias_actuales = existencias_anteriores - cantidad_vendida
        respaldo_anterior.append((producto_id, existencias_anteriores))
        resumen_descuento.append({
            "producto_id": producto_id,
            "cantidad_vendida": cantidad_vendida,
            "existencias_anteriores": existencias_anteriores,
            "existencias_actuales": existencias_actuales
        })

    # APLICAR EL DESCUENTO DE MANERA CONSISTENTE CON REVERSIÓN SI OCURRE UN ERROR
    aplicados: list[tuple[int, int]] = []
    try:
        for item_resumen in resumen_descuento:
            producto_id = item_resumen["producto_id"]
            existencias_anteriores = item_resumen["existencias_anteriores"]
            existencias_actuales = item_resumen["existencias_actuales"]

            resultado = inventarioRepositorio.ActualizarCantidadInventarioRepositorio(
                producto_id,
                existencias_actuales
            )
            if resultado is None:
                raise RuntimeError(
                    f"No fue posible actualizar el inventario del producto ID {producto_id}"
                )

            aplicados.append((producto_id, existencias_anteriores))

    except Exception:
        # REVERTIR CUALQUIER DESCUENTO PARCIAL PARA MANTENER LA CONSISTENCIA
        for producto_id, cantidad_previa in aplicados:
            inventarioRepositorio.ActualizarCantidadInventarioRepositorio(
                producto_id,
                cantidad_previa
            )
        raise

    return resumen_descuento
