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
