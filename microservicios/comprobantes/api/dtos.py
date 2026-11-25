from pydantic import BaseModel, Field, ConfigDict, field_validator


# DTO PARA SOLICITAR LA GENERACIÓN DE UN COMPROBANTE DE VENTA
class ComprobanteRegistro(BaseModel):

    venta_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DE LA VENTA CONFIRMADA PARA GENERAR EL COMPROBANTE",
        examples=[1]
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # VALIDAR QUE EL IDENTIFICADOR DE LA VENTA SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("venta_id", mode="before")
    @classmethod
    def ValidarVentaId(cls, valor):
        if isinstance(valor, bool) or isinstance(valor, float) or valor is None:
            raise ValueError("EL IDENTIFICADOR DE LA VENTA DEBE SER UN NÚMERO ENTERO POSITIVO.")
        if isinstance(valor, str):
            raise ValueError("EL IDENTIFICADOR DE LA VENTA DEBE SER UN NÚMERO ENTERO POSITIVO.")
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("EL IDENTIFICADOR DE LA VENTA DEBE SER UN NÚMERO ENTERO POSITIVO.")
        return valor
