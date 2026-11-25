from microservicios.clientes.servicio import clienteServicio
from microservicios.inventario.repositorio import inventarioRepositorio
from microservicios.inventario.servicio import inventarioServicio
from microservicios.productos.servicio import productoServicio
from microservicios.ventas.repositorio import ventaRepositorio


# REGISTRAR UNA NUEVA VENTA EN ESTADO PENDIENTE ASOCIADA A UN CLIENTE
def RegistrarVentaDominio(datos_venta: dict) -> dict:

    # VERIFICAR QUE EL CLIENTE SELECCIONADO EXISTA EN EL SISTEMA
    cliente_existente = clienteServicio.ObtenerClientePorIdServicio(
        datos_venta["cliente_id"]
    )

    if cliente_existente is None:
        raise LookupError("El cliente seleccionado no existe")

    # VERIFICAR QUE LOS PRODUCTOS INICIALES EXISTAN SI SE PROPORCIONAN
    for item in datos_venta.get("productos", []):
        producto_existente = productoServicio.ObtenerProductoPorIdServicio(
            item["producto_id"]
        )
        if producto_existente is None:
            raise LookupError(f"El producto con ID {item['producto_id']} no existe")

    venta_registrada = ventaRepositorio.RegistrarVentaRepositorio(datos_venta)

    return {
        "venta_id": venta_registrada["id"],
        "cliente_id": venta_registrada["cliente_id"],
        "estado": venta_registrada["estado"],
        "productos": venta_registrada["productos"]
    }


# CONSULTAR TODAS LAS VENTAS REGISTRADAS
def ConsultarVentasDominio() -> list[dict]:
    return ventaRepositorio.ConsultarVentasRepositorio()


# CONSULTAR UNA VENTA POR SU IDENTIFICADOR
def ObtenerVentaPorIdDominio(venta_id: int) -> dict | None:
    return ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)


# HELPER PARA OBTENER UNA VENTA PENDIENTE DE MODIFICACIÓN
def _ObtenerVentaPendiente(venta_id: int) -> dict:

    venta = ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    if venta["estado"] != "pendiente":
        raise ValueError("No se puede modificar el detalle de una venta que ya fue confirmada")

    return venta


# AGREGAR UN PRODUCTO Y SU CANTIDAD AL DETALLE DE UNA VENTA PENDIENTE
def AgregarDetalleVentaDominio(venta_id: int, datos_detalle: dict) -> dict:

    _ObtenerVentaPendiente(venta_id)

    producto_id = datos_detalle["producto_id"]
    producto_existente = productoServicio.ObtenerProductoPorIdServicio(producto_id)

    if producto_existente is None:
        raise LookupError("El producto seleccionado no existe")

    detalle = ventaRepositorio.AgregarDetalleVentaRepositorio(
        venta_id,
        producto_id,
        datos_detalle["cantidad"]
    )

    return {
        "venta_id": venta_id,
        "producto_id": detalle["producto_id"],
        "cantidad": detalle["cantidad"]
    }


# CONSULTAR EL DETALLE DE PRODUCTOS Y CANTIDADES DE UNA VENTA
def ConsultarDetalleVentaDominio(venta_id: int) -> list[dict]:

    venta = ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    detalle_enriquecido = []
    for item in venta["productos"]:
        producto = productoServicio.ObtenerProductoPorIdServicio(item["producto_id"])
        detalle_enriquecido.append({
            "producto_id": item["producto_id"],
            "nombre_producto": producto["nombre"] if producto else None,
            "codigo_producto": producto["codigo"] if producto else None,
            "precio": producto["precio"] if producto else None,
            "cantidad": item["cantidad"]
        })

    return detalle_enriquecido


# MODIFICAR LA CANTIDAD DE UN PRODUCTO EN EL DETALLE DE UNA VENTA PENDIENTE
def ActualizarDetalleVentaDominio(
    venta_id: int,
    producto_id: int,
    nueva_cantidad: int
) -> dict:

    _ObtenerVentaPendiente(venta_id)

    detalle = ventaRepositorio.ActualizarCantidadDetalleVentaRepositorio(
        venta_id,
        producto_id,
        nueva_cantidad
    )

    if detalle is None:
        raise LookupError("El producto no se encuentra en el detalle de la venta")

    return {
        "venta_id": venta_id,
        "producto_id": producto_id,
        "cantidad": detalle["cantidad"]
    }


# RETIRAR UN PRODUCTO DEL DETALLE DE UNA VENTA PENDIENTE
def EliminarDetalleVentaDominio(venta_id: int, producto_id: int) -> dict:

    _ObtenerVentaPendiente(venta_id)

    eliminado = ventaRepositorio.EliminarDetalleVentaRepositorio(
        venta_id,
        producto_id
    )

    if not eliminado:
        raise LookupError("El producto no se encuentra en el detalle de la venta")

    return {
        "venta_id": venta_id,
        "producto_id": producto_id
    }


# CONFIRMAR UNA VENTA Y DESCONTAR EXISTENCIAS DEL INVENTARIO DE FORMA CONSISTENTE
def ConfirmarVentaDominio(venta_id: int) -> dict:

    # VERIFICAR QUE LA VENTA EXISTA
    venta = ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    # EVITAR DESCUENTOS DUPLICADOS SI LA VENTA YA FUE CONFIRMADA
    if venta["estado"] == "confirmada":
        raise ValueError("La venta ya fue confirmada y sus existencias ya fueron descontadas")

    # IMPEDIR CONTINUAR SI LA VENTA NO TIENE PRODUCTOS EN SU DETALLE
    if not venta["productos"]:
        raise ValueError("Debe agregar al menos un producto al detalle de la venta")

    # VALIDAR DISPONIBILIDAD ANTES DE REALIZAR CUALQUIER DESCUENTO
    productos_para_validar = [
        {
            "producto_id": item["producto_id"],
            "cantidad_solicitada": item["cantidad"]
        }
        for item in venta["productos"]
    ]
    validacion = inventarioServicio.ValidarDisponibilidadServicio(
        productos_para_validar
    )

    if not validacion["disponibilidad_suficiente"]:
        insuficientes = [
            f"producto ID {p['producto_id']} (solicitado: {p['cantidad_solicitada']}, disponible: {p['cantidad_disponible']})"
            for p in validacion["productos"]
            if not p["disponible"]
        ]
        raise ValueError(
            "No hay suficiente inventario para completar la operación: "
            + ", ".join(insuficientes)
        )

    # DESCONTAR EXISTENCIAS DEL INVENTARIO PARA LA VENTA CONFIRMADA
    resumen_descuento = inventarioServicio.DescontarExistenciasVentaServicio(
        venta["productos"],
        "confirmada"
    )

    # ACTUALIZAR EL ESTADO DE LA VENTA A CONFIRMADA CON REVERSIÓN SI FALLA
    try:
        venta_actualizada = ventaRepositorio.ActualizarEstadoVentaRepositorio(
            venta_id,
            "confirmada"
        )
        if venta_actualizada is None:
            raise RuntimeError("No fue posible actualizar el estado de la venta")
    except Exception:
        # REVERTIR EL DESCUENTO DEL INVENTARIO SI FALLA LA CONFIRMACIÓN DE LA VENTA
        for item in resumen_descuento:
            inventarioRepositorio.ActualizarCantidadInventarioRepositorio(
                item["producto_id"],
                item["existencias_anteriores"]
            )
        raise

    return {
        "venta_id": venta_id,
        "estado": "confirmada",
        "productos": resumen_descuento
    }
