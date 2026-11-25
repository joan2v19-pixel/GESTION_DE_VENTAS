from microservicios.ventas.dominio import ventaDominio


# SERVICIO PARA REGISTRAR UNA VENTA EN ESTADO PENDIENTE
def RegistrarVentaServicio(datos_venta: dict) -> dict:
    return ventaDominio.RegistrarVentaDominio(datos_venta)


# SERVICIO PARA CONSULTAR TODAS LAS VENTAS
def ConsultarVentasServicio() -> list[dict]:
    return ventaDominio.ConsultarVentasDominio()


# SERVICIO PARA CONSULTAR UNA VENTA POR ID
def ObtenerVentaPorIdServicio(venta_id: int) -> dict | None:
    return ventaDominio.ObtenerVentaPorIdDominio(venta_id)


# SERVICIO PARA CONFIRMAR UNA VENTA Y DESCONTAR EXISTENCIAS
def ConfirmarVentaServicio(venta_id: int) -> dict:
    return ventaDominio.ConfirmarVentaDominio(venta_id)


# SERVICIO PARA AGREGAR UN PRODUCTO AL DETALLE DE UNA VENTA
def AgregarDetalleVentaServicio(venta_id: int, datos_detalle: dict) -> dict:
    return ventaDominio.AgregarDetalleVentaDominio(venta_id, datos_detalle)


# SERVICIO PARA CONSULTAR EL DETALLE DE UNA VENTA
def ConsultarDetalleVentaServicio(venta_id: int) -> list[dict]:
    return ventaDominio.ConsultarDetalleVentaDominio(venta_id)


# SERVICIO PARA MODIFICAR LA CANTIDAD DE UN PRODUCTO EN EL DETALLE
def ActualizarDetalleVentaServicio(
    venta_id: int,
    producto_id: int,
    nueva_cantidad: int
) -> dict:
    return ventaDominio.ActualizarDetalleVentaDominio(
        venta_id,
        producto_id,
        nueva_cantidad
    )


# SERVICIO PARA RETIRAR UN PRODUCTO DEL DETALLE DE UNA VENTA
def EliminarDetalleVentaServicio(venta_id: int, producto_id: int) -> dict:
    return ventaDominio.EliminarDetalleVentaDominio(venta_id, producto_id)
