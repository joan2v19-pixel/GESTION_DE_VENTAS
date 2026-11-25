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


# CONFIRMAR UNA VENTA Y DESCONTAR EXISTENCIAS DEL INVENTARIO DE FORMA CONSISTENTE
def ConfirmarVentaDominio(venta_id: int) -> dict:

    # VERIFICAR QUE LA VENTA EXISTA
    venta = ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    # EVITAR DESCUENTOS DUPLICADOS SI LA VENTA YA FUE CONFIRMADA
    if venta["estado"] == "confirmada":
        raise ValueError("La venta ya fue confirmada y sus existencias ya fueron descontadas")

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
