from datetime import datetime


# LISTA PARA ALMACENAR LOS COMPROBANTES GENERADOS EN MEMORIA
comprobantes = []


# REGISTRAR UN NUEVO COMPROBANTE ASOCIADO A UNA VENTA CONFIRMADA
def RegistrarComprobanteRepositorio(datos_comprobante: dict) -> dict:

    nuevo_comprobante = {
        "comprobante_id": len(comprobantes) + 1,
        "venta_id": datos_comprobante["venta_id"],
        "fecha_emision": datetime.now().isoformat(),
        "cliente": datos_comprobante["cliente"],
        "productos": datos_comprobante["productos"],
        "total": datos_comprobante["total"]
    }

    comprobantes.append(nuevo_comprobante)

    return nuevo_comprobante


# CONSULTAR TODOS LOS COMPROBANTES REGISTRADOS
def ConsultarComprobantesRepositorio() -> list[dict]:
    return comprobantes


# CONSULTAR UN COMPROBANTE POR SU IDENTIFICADOR
def ObtenerComprobantePorIdRepositorio(comprobante_id: int) -> dict | None:

    for comprobante in comprobantes:
        if comprobante["comprobante_id"] == comprobante_id:
            return comprobante

    return None
