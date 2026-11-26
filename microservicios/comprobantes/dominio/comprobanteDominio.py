from microservicios.comprobantes.repositorio import comprobanteRepositorio
from microservicios.ventas.servicio import ventaServicio


# GENERAR UN COMPROBANTE A PARTIR DE UNA VENTA CONFIRMADA
def GenerarComprobanteDominio(venta_id: int) -> dict:

    # CONSULTAR LA VENTA ASOCIADA
    venta = ventaServicio.ObtenerVentaPorIdServicio(venta_id)

    if venta is None:
        raise LookupError("La venta seleccionada no existe")

    # VERIFICAR QUE LA VENTA SE ENCUENTRE CONFIRMADA
    if venta.get("estado") != "confirmada":
        raise ValueError("La venta debe estar confirmada para generar el comprobante")

    # VALIDAR QUE LA INFORMACIÓN DEL CLIENTE ESTÉ COMPLETA
    cliente = venta.get("cliente") or {}
    if not cliente.get("nombre") or not cliente.get("identificacion"):
        raise ValueError(
            "Faltan datos del cliente requeridos para generar el comprobante"
        )

    # VALIDAR QUE EXISTAN PRODUCTOS CON INFORMACIÓN COMPLETA
    productos_venta = venta.get("productos") or []
    if not productos_venta:
        raise ValueError(
            "Faltan los productos de la venta para generar el comprobante"
        )

    productos_comprobante = []
    for producto in productos_venta:
        if (
            not producto.get("nombre")
            or producto.get("cantidad") is None
            or producto.get("cantidad") <= 0
            or producto.get("subtotal") is None
            or producto.get("subtotal") <= 0
        ):
            raise ValueError(
                "Faltan datos válidos de los productos para generar el comprobante"
            )

        productos_comprobante.append({
            "nombre": producto["nombre"],
            "cantidad": producto["cantidad"],
            "precio_unitario": producto.get("precio_unitario"),
            "subtotal": producto["subtotal"]
        })

    # VALIDAR EL VALOR TOTAL DE LA VENTA
    total_venta = venta.get("total")
    if total_venta is None or total_venta <= 0:
        raise ValueError("El total de la venta no es válido para generar el comprobante")

    # GUARDAR Y RETORNAR EL COMPROBANTE GENERADO
    return comprobanteRepositorio.RegistrarComprobanteRepositorio({
        "venta_id": venta_id,
        "cliente": {
            "nombre": cliente["nombre"],
            "identificacion": cliente["identificacion"]
        },
        "productos": productos_comprobante,
        "total": total_venta
    })


# CONSULTAR TODOS LOS COMPROBANTES REGISTRADOS
def ConsultarComprobantesDominio() -> list[dict]:
    return comprobanteRepositorio.ConsultarComprobantesRepositorio()


# CONSULTAR UN COMPROBANTE POR SU IDENTIFICADOR VERIFICANDO SU VENTA ASOCIADA
def ObtenerComprobantePorIdDominio(comprobante_id: int) -> dict | None:
    comprobante = comprobanteRepositorio.ObtenerComprobantePorIdRepositorio(
        comprobante_id
    )
    if comprobante is None:
        return None

    # VERIFICAR QUE EL COMPROBANTE ESTÉ ASOCIADO A UNA VENTA REGISTRADA
    venta = ventaServicio.ObtenerVentaPorIdServicio(comprobante["venta_id"])
    if venta is None:
        raise LookupError("La venta asociada al comprobante no existe")

    return comprobante
