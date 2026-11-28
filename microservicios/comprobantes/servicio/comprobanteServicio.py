from microservicios.comprobantes.dominio import comprobanteDominio


# SERVICIO PARA GENERAR UN COMPROBANTE DE VENTA
def GenerarComprobanteServicio(venta_id: int) -> dict:
    return comprobanteDominio.GenerarComprobanteDominio(venta_id)


# SERVICIO PARA CONSULTAR TODOS LOS COMPROBANTES
def ConsultarComprobantesServicio() -> list[dict]:
    return comprobanteDominio.ConsultarComprobantesDominio()


# SERVICIO PARA CONSULTAR UN COMPROBANTE POR ID
def ObtenerComprobantePorIdServicio(comprobante_id: int) -> dict | None:
    return comprobanteDominio.ObtenerComprobantePorIdDominio(comprobante_id)
