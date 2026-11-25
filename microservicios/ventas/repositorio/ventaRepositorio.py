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


# AGREGAR UN PRODUCTO AL DETALLE DE UNA VENTA EXISTENTE
def AgregarDetalleVentaRepositorio(
    venta_id: int,
    producto_id: int,
    cantidad: int
) -> dict | None:

    venta = ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        return None

    for item in venta["productos"]:
        if item["producto_id"] == producto_id:
            item["cantidad"] += cantidad
            return item

    nuevo_detalle = {
        "producto_id": producto_id,
        "cantidad": cantidad
    }
    venta["productos"].append(nuevo_detalle)

    return nuevo_detalle


# ACTUALIZAR LA CANTIDAD DE UN PRODUCTO EN EL DETALLE DE UNA VENTA
def ActualizarCantidadDetalleVentaRepositorio(
    venta_id: int,
    producto_id: int,
    nueva_cantidad: int
) -> dict | None:

    venta = ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        return None

    for item in venta["productos"]:
        if item["producto_id"] == producto_id:
            item["cantidad"] = nueva_cantidad
            return item

    return None


# RETIRAR UN PRODUCTO DEL DETALLE DE UNA VENTA
def EliminarDetalleVentaRepositorio(venta_id: int, producto_id: int) -> bool:

    venta = ObtenerVentaPorIdRepositorio(venta_id)

    if venta is None:
        return False

    for indice, item in enumerate(venta["productos"]):
        if item["producto_id"] == producto_id:
            venta["productos"].pop(indice)
            return True

    return False
