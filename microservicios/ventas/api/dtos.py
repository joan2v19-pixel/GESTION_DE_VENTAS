from pydantic import BaseModel, Field, ConfigDict, field_validator


# HELPER PARA VALIDAR ENTEROS POSITIVOS ESTRICTOS
def _ValidarEnteroPositivo(valor, mensaje_error: str) -> int:
    if isinstance(valor, bool) or isinstance(valor, float) or valor is None:
        raise ValueError(mensaje_error)
    if isinstance(valor, str):
        raise ValueError(mensaje_error)
    if not isinstance(valor, int) or valor <= 0:
        raise ValueError(mensaje_error)
    return valor


# DTO PARA CADA PRODUCTO INCLUIDO EN UNA VENTA
class VentaProductoItem(BaseModel):

    producto_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DEL PRODUCTO VENDIDO",
        examples=[1]
    )
    cantidad: int = Field(
        ...,
        gt=0,
        description="CANTIDAD VENDIDA DEL PRODUCTO (ENTERO MAYOR A CERO)",
        examples=[5]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DEL PRODUCTO SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("producto_id", mode="before")
    @classmethod
    def ValidarProductoId(cls, valor):
        return _ValidarEnteroPositivo(
            valor,
            "EL IDENTIFICADOR DEL PRODUCTO DEBE SER UN NÚMERO ENTERO POSITIVO."
        )

    # VALIDAR QUE LA CANTIDAD VENDIDA SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("cantidad", mode="before")
    @classmethod
    def ValidarCantidad(cls, valor):
        return _ValidarEnteroPositivo(
            valor,
            "LA CANTIDAD DEBE SER UN NÚMERO ENTERO MAYOR A CERO."
        )


# DTO PARA REGISTRAR UNA VENTA EN ESTADO PENDIENTE
class VentaRegistro(BaseModel):

    productos: list[VentaProductoItem] = Field(
        ...,
        min_length=1,
        description="LISTADO DE PRODUCTOS Y CANTIDADES DE LA VENTA"
    )

    model_config = ConfigDict(
        extra="forbid"
    )


# DTO PARA CONFIRMAR UNA VENTA REGISTRADA
class ConfirmarVentaSolicitud(BaseModel):

    venta_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DE LA VENTA A CONFIRMAR",
        examples=[1]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DE LA VENTA SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("venta_id", mode="before")
    @classmethod
    def ValidarVentaId(cls, valor):
        return _ValidarEnteroPositivo(
            valor,
            "EL IDENTIFICADOR DE LA VENTA DEBE SER UN NÚMERO ENTERO POSITIVO."
        )
