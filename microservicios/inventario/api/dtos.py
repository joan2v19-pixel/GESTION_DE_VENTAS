from pydantic import BaseModel, Field, ConfigDict, field_validator


# HELPER PARA VALIDAR ENTEROS ESTRICTOS SIN BOOLEANOS, DECIMALES NI STRINGS
def _ValidarEnteroEstricto(valor, minimo: int, mensaje_error: str) -> int:
    if isinstance(valor, bool) or isinstance(valor, float) or valor is None:
        raise ValueError(mensaje_error)
    if isinstance(valor, str):
        raise ValueError(mensaje_error)
    if not isinstance(valor, int) or valor < minimo:
        raise ValueError(mensaje_error)
    return valor


# DTO PARA REGISTRAR EXISTENCIAS INICIALES DE UN PRODUCTO
class ExistenciasInicialesRegistro(BaseModel):

    producto_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DEL PRODUCTO REGISTRADO",
        examples=[1]
    )
    cantidad_inicial: int = Field(
        ...,
        ge=0,
        description="CANTIDAD INICIAL DISPONIBLE DEL PRODUCTO (ENTERO MAYOR O IGUAL A CERO)",
        examples=[100]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DEL PRODUCTO SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("producto_id", mode="before")
    @classmethod
    def ValidarProductoId(cls, valor):
        return _ValidarEnteroEstricto(
            valor,
            1,
            "EL IDENTIFICADOR DEL PRODUCTO DEBE SER UN NÚMERO ENTERO POSITIVO."
        )

    # VALIDAR QUE LA CANTIDAD INICIAL SEA UN NÚMERO ENTERO MAYOR O IGUAL A CERO
    @field_validator("cantidad_inicial", mode="before")
    @classmethod
    def ValidarCantidadInicial(cls, valor):
        return _ValidarEnteroEstricto(
            valor,
            0,
            "LA CANTIDAD INICIAL DEBE SER UN NÚMERO ENTERO MAYOR O IGUAL A CERO."
        )


# DTO PARA CADA PRODUCTO INCLUIDO EN LA VALIDACIÓN DE DISPONIBILIDAD
class ProductoValidacionItem(BaseModel):

    producto_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DEL PRODUCTO A VALIDAR",
        examples=[1]
    )
    cantidad_solicitada: int = Field(
        ...,
        gt=0,
        description="CANTIDAD SOLICITADA PARA LA VENTA (ENTERO MAYOR A CERO)",
        examples=[5]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DEL PRODUCTO SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("producto_id", mode="before")
    @classmethod
    def ValidarProductoId(cls, valor):
        return _ValidarEnteroEstricto(
            valor,
            1,
            "EL IDENTIFICADOR DEL PRODUCTO DEBE SER UN NÚMERO ENTERO POSITIVO."
        )

    # VALIDAR QUE LA CANTIDAD SOLICITADA SEA UN ENTERO MAYOR A CERO
    @field_validator("cantidad_solicitada", mode="before")
    @classmethod
    def ValidarCantidadSolicitada(cls, valor):
        return _ValidarEnteroEstricto(
            valor,
            1,
            "LA CANTIDAD SOLICITADA DEBE SER UN NÚMERO ENTERO MAYOR A CERO."
        )


# DTO PARA SOLICITAR LA VALIDACIÓN DE DISPONIBILIDAD DE UNA VENTA
class ValidacionDisponibilidadSolicitud(BaseModel):

    productos: list[ProductoValidacionItem] = Field(
        ...,
        min_length=1,
        description="LISTADO DE PRODUCTOS Y CANTIDADES SOLICITADAS PARA VALIDAR"
    )

    model_config = ConfigDict(
        extra="forbid"
    )
