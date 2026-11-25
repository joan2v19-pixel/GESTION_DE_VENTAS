# LISTA PARA ALMACENAR LAS VENTAS EN MEMORIA
ventas = []


# REGISTRAR UNA NUEVA VENTA EN ESTADO PENDIENTE
def RegistrarVentaRepositorio(datos_venta: dict) -> dict:

    nueva_venta = {
        "id": len(ventas) + 1,
        "cliente_id": datos_venta["cliente_id"],
        "estado": "pendiente",
        "productos": datos_venta.get("productos", [])
    }

    ventas.append(nueva_venta)

    return nueva_venta


# CONSULTAR TODAS LAS VENTAS REGISTRADAS
def ConsultarVentasRepositorio() -> list[dict]:
    return ventas


# CONSULTAR UNA VENTA POR SU IDENTIFICADOR
def ObtenerVentaPorIdRepositorio(venta_id: int) -> dict | None:

    for venta in ventas:
        if venta["id"] == venta_id:
            return venta

    return None


# ACTUALIZAR EL ESTADO DE UNA VENTA EXISTENTE
def ActualizarEstadoVentaRepositorio(venta_id: int, nuevo_estado: str) -> dict | None:

    venta = ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        return None

    venta["estado"] = nuevo_estado

    return venta
