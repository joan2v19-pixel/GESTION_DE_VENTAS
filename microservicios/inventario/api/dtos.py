from pydantic import BaseModel, Field, ConfigDict, field_validator


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
        if isinstance(valor, bool) or isinstance(valor, float) or valor is None:
            raise ValueError("EL IDENTIFICADOR DEL PRODUCTO DEBE SER UN NÚMERO ENTERO POSITIVO.")
        if isinstance(valor, str):
            raise ValueError("EL IDENTIFICADOR DEL PRODUCTO DEBE SER UN NÚMERO ENTERO POSITIVO.")
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("EL IDENTIFICADOR DEL PRODUCTO DEBE SER UN NÚMERO ENTERO POSITIVO.")
        return valor

    # VALIDAR QUE LA CANTIDAD INICIAL SEA UN NÚMERO ENTERO MAYOR O IGUAL A CERO
    @field_validator("cantidad_inicial", mode="before")
    @classmethod
    def ValidarCantidadInicial(cls, valor):
        if isinstance(valor, bool) or isinstance(valor, float) or valor is None:
            raise ValueError("LA CANTIDAD INICIAL DEBE SER UN NÚMERO ENTERO MAYOR O IGUAL A CERO.")
        if isinstance(valor, str):
            raise ValueError("LA CANTIDAD INICIAL DEBE SER UN NÚMERO ENTERO MAYOR O IGUAL A CERO.")
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("LA CANTIDAD INICIAL DEBE SER UN NÚMERO ENTERO MAYOR O IGUAL A CERO.")
        return valor
