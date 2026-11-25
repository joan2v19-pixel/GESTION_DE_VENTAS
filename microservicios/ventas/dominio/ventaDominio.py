from datetime import datetime
import math

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


# CALCULAR SUBTOTALES Y TOTAL DE UNA VENTA
def CalcularTotalesVentaDominio(venta_id: int) -> dict:

    # VERIFICAR QUE LA VENTA EXISTA
    venta = ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    # IMPEDIR CALCULAR SI NO HAY PRODUCTOS EN EL DETALLE
    if not venta["productos"]:
        raise ValueError("Debe agregar al menos un producto al detalle de la venta")

    productos_calculados = []

    for item in venta["productos"]:
        producto_id = item["producto_id"]
        cantidad = item["cantidad"]

        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError(
                f"La cantidad del producto ID {producto_id} no es válida para el cálculo"
            )

        producto = productoServicio.ObtenerProductoPorIdServicio(producto_id)
        if producto is None:
            raise LookupError(f"El producto con ID {producto_id} no existe")

        precio_unitario = producto.get("precio")
        if (
            isinstance(precio_unitario, bool)
            or not isinstance(precio_unitario, (int, float))
            or not math.isfinite(precio_unitario)
            or precio_unitario <= 0
        ):
            raise ValueError(
                f"El producto '{producto['nombre']}' presenta un problema con su precio"
            )

        precio_redondeado = round(float(precio_unitario), 2)
        subtotal = round(precio_redondeado * cantidad, 2)

        productos_calculados.append({
            "producto_id": producto_id,
            "nombre": producto["nombre"],
            "precio_unitario": precio_redondeado,
            "cantidad": cantidad,
            "subtotal": subtotal
        })

    total_venta = round(sum(p["subtotal"] for p in productos_calculados), 2)

    return {
        "venta_id": venta_id,
        "productos": productos_calculados,
        "total_venta": total_venta
    }


# VALIDAR DISPONIBILIDAD DE INVENTARIO PARA UNA VENTA ANTES DE CONFIRMARLA
def ValidarInventarioVentaDominio(
    venta_id: int,
    productos_solicitud: list[dict] | None = None
) -> dict:

    # VERIFICAR QUE LA VENTA EXISTA
    venta = ventaRepositorio.ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    productos_a_validar = (
        productos_solicitud if productos_solicitud is not None else venta["productos"]
    )

    if not productos_a_validar:
        raise ValueError("Debe agregar al menos un producto al detalle de la venta")

    # AGRUPAR CANTIDADES POR PRODUCTO PARA VALIDAR EL TOTAL SOLICITADO
    cantidades_por_producto: dict[int, int] = {}
    for item in productos_a_validar:
        producto_id = item["producto_id"]
        cantidades_por_producto[producto_id] = (
            cantidades_por_producto.get(producto_id, 0) + item["cantidad"]
        )

    consulta_disponibilidad = [
        {
            "producto_id": producto_id,
            "cantidad_solicitada": cantidad_total
        }
        for producto_id, cantidad_total in cantidades_por_producto.items()
    ]

    resultado = inventarioServicio.ValidarDisponibilidadServicio(
        consulta_disponibilidad
    )

    productos_formateados = [
        {
            "producto_id": item["producto_id"],
            "cantidad_solicitada": item["cantidad_solicitada"],
            "existencias_disponibles": item["cantidad_disponible"],
            "disponible": item["disponible"]
        }
        for item in resultado["productos"]
    ]

    return {
        "venta_id": venta_id,
        "disponibilidad_suficiente": resultado["disponibilidad_suficiente"],
        "productos": productos_formateados
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

    # VERIFICAR QUE EL CLIENTE ASOCIADO EXISTA EN EL SISTEMA
    cliente_existente = clienteServicio.ObtenerClientePorIdServicio(
        venta["cliente_id"]
    )
    if cliente_existente is None:
        raise LookupError("El cliente asociado a la venta no existe")

    # IMPEDIR CONTINUAR SI LA VENTA NO TIENE PRODUCTOS EN SU DETALLE
    if not venta["productos"]:
        raise ValueError("Debe agregar al menos un producto al detalle de la venta")

    # CALCULAR TOTALES PARA VALIDAR PRECIOS Y REGISTRAR EL IMPORTE TOTAL
    totales_venta = CalcularTotalesVentaDominio(venta_id)

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

    fecha_confirmacion = datetime.now().isoformat()

    # ACTUALIZAR EL ESTADO DE LA VENTA A CONFIRMADA CON REVERSIÓN SI FALLA
    try:
        venta_actualizada = ventaRepositorio.ActualizarEstadoVentaRepositorio(
            venta_id,
            "confirmada",
            {
                "fecha_confirmacion": fecha_confirmacion,
                "subtotal": totales_venta["total_venta"],
                "total": totales_venta["total_venta"],
                "detalle_totales": totales_venta["productos"]
            }
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
        "cliente_id": venta["cliente_id"],
        "fecha_confirmacion": fecha_confirmacion,
        "subtotal": totales_venta["total_venta"],
        "total": totales_venta["total_venta"],
        "total_venta": totales_venta["total_venta"],
        "inventario_actualizado": True,
        "productos": resumen_descuento
    }
