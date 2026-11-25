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


# DTO PARA REGISTRAR UNA VENTA EN ESTADO PENDIENTE ASOCIADA A UN CLIENTE
class VentaRegistro(BaseModel):

    cliente_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DEL CLIENTE ASOCIADO A LA VENTA",
        examples=[1]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DEL CLIENTE SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("cliente_id", mode="before")
    @classmethod
    def ValidarClienteId(cls, valor):
        return _ValidarEnteroPositivo(
            valor,
            "EL CLIENTE ES OBLIGATORIO Y SU IDENTIFICADOR DEBE SER UN NÚMERO ENTERO POSITIVO."
        )


# DTO PARA CONFIRMAR UNA VENTA REGISTRADA
class ConfirmarVentaSolicitud(BaseModel):

    venta_id: int | None = Field(
        default=None,
        gt=0,
        description="IDENTIFICADOR OPCIONAL DE LA VENTA A CONFIRMAR",
        examples=[1]
    )
    confirmar: bool | None = Field(
        default=True,
        description="INDICADOR BOOLEANO PARA CONFIRMAR LA VENTA",
        examples=[True]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DE LA VENTA SEA UN ENTERO POSITIVO VÁLIDO SI SE ENVÍA
    @field_validator("venta_id", mode="before")
    @classmethod
    def ValidarVentaId(cls, valor):
        if valor is None:
            return None
        return _ValidarEnteroPositivo(
            valor,
            "EL IDENTIFICADOR DE LA VENTA DEBE SER UN NÚMERO ENTERO POSITIVO."
        )


# DTO PARA AGREGAR UN PRODUCTO AL DETALLE DE UNA VENTA
class DetalleVentaAgregar(VentaProductoItem):
    pass


# DTO PARA ACTUALIZAR LA CANTIDAD DE UN PRODUCTO EN EL DETALLE DE UNA VENTA
class DetalleVentaActualizar(BaseModel):

    cantidad: int = Field(
        ...,
        gt=0,
        description="NUEVA CANTIDAD DEL PRODUCTO EN EL DETALLE (ENTERO MAYOR A CERO)",
        examples=[5]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE LA CANTIDAD SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("cantidad", mode="before")
    @classmethod
    def ValidarCantidad(cls, valor):
        return _ValidarEnteroPositivo(
            valor,
            "LA CANTIDAD DEBE SER UN NÚMERO ENTERO MAYOR A CERO."
        )


# DTO PARA VALIDAR INVENTARIO DE UNA VENTA ANTES DE CONFIRMARLA
class ValidarInventarioVentaSolicitud(BaseModel):

    productos: list[VentaProductoItem] | None = Field(
        default=None,
        min_length=1,
        description="LISTADO OPCIONAL DE PRODUCTOS Y CANTIDADES A VALIDAR"
    )

    model_config = ConfigDict(
        extra="forbid"
    )
