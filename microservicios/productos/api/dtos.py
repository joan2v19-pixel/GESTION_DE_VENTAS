from pydantic import BaseModel, Field, ConfigDict, field_validator
import math
import re


# PALABRAS RESERVADAS O DE PRUEBA POR DEFECTO QUE NO SE DEBEN PERMITIR
PALABRAS_PROHIBIDAS = {"string", "null", "none", "undefined"}


# VALIDAR QUE UN TEXTO NO SEA VACÍO NI CONTENGA PALABRAS DE PRUEBA POR DEFECTO
def ValidarTextoNoVacioNiPorDefecto(valor: str, nombre_campo: str) -> str:
    texto_limpio = valor.strip()
    if not texto_limpio:
        raise ValueError(f"EL CAMPO {nombre_campo} NO PUEDE ESTAR VACÍO.")
    if texto_limpio.lower() in PALABRAS_PROHIBIDAS:
        raise ValueError(f"EL CAMPO {nombre_campo} NO PUEDE CONTENER EL VALOR '{texto_limpio}'.")
    return texto_limpio


# DTO PARA REGISTRAR UN PRODUCTO
class ProductoRegistro(BaseModel):

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="NOMBRE DEL PRODUCTO A REGISTRAR (SOLO LETRAS Y ESPACIOS)",
        examples=["Arroz"]
    )
    codigo: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="CÓDIGO ÚNICO DEL PRODUCTO",
        examples=["PROD-001"]
    )
    precio: float = Field(
        ...,
        description="PRECIO DE VENTA DEL PRODUCTO (DEBE SER UN NÚMERO MAYOR A 0)",
        examples=[3500]
    )
    categoria_id: int = Field(
        ...,
        gt=0,
        description="IDENTIFICADOR DE LA CATEGORÍA ASOCIADA",
        examples=[1]
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    # VALIDAR QUE EL NOMBRE DEL PRODUCTO NO ESTÉ VACÍO, NO SEA 'string' Y NO CONTENGA NÚMEROS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor: str) -> str:
        valor = ValidarTextoNoVacioNiPorDefecto(valor, "NOMBRE")
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError(
                "EL NOMBRE DEL PRODUCTO SOLO DEBE CONTENER LETRAS Y ESPACIOS (NO SE PERMITEN NÚMEROS NI SÍMBOLOS)."
            )
        return valor

    # VALIDAR QUE EL CÓDIGO DEL PRODUCTO NO ESTÉ VACÍO, NO SEA 'string' Y TENGA FORMATO VÁLIDO
    @field_validator("codigo")
    @classmethod
    def ValidarCodigo(cls, valor: str) -> str:
        valor = ValidarTextoNoVacioNiPorDefecto(valor, "CÓDIGO")
        if not re.fullmatch(r"[a-zA-Z0-9\-_]+", valor) or not any(c.isalnum() for c in valor):
            raise ValueError(
                "EL CÓDIGO DEL PRODUCTO SOLO DEBE CONTENER LETRAS, NÚMEROS, GUIONES O GUIONES BAJOS."
            )
        return valor

    # VALIDAR QUE EL PRECIO SEA UN NÚMERO VÁLIDO Y MAYOR QUE CERO
    @field_validator("precio", mode="before")
    @classmethod
    def ValidarPrecio(cls, valor):
        if isinstance(valor, bool) or valor is None:
            raise ValueError("EL PRECIO DEBE SER UN VALOR NUMÉRICO VÁLIDO.")
        if isinstance(valor, str) and (not valor.strip() or valor.strip().lower() in PALABRAS_PROHIBIDAS):
            raise ValueError("EL PRECIO DEBE SER UN VALOR NUMÉRICO VÁLIDO.")
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError("EL PRECIO DEBE SER UN VALOR NUMÉRICO VÁLIDO.")
        if not math.isfinite(numero) or numero <= 0:
            raise ValueError("EL PRECIO DEL PRODUCTO DEBE SER MAYOR A CERO.")
        return numero

    # VALIDAR QUE EL IDENTIFICADOR DE CATEGORÍA SEA UN ENTERO POSITIVO VÁLIDO
    @field_validator("categoria_id", mode="before")
    @classmethod
    def ValidarCategoriaId(cls, valor):
        if isinstance(valor, bool) or isinstance(valor, float) or valor is None:
            raise ValueError("EL IDENTIFICADOR DE LA CATEGORÍA DEBE SER UN NÚMERO ENTERO POSITIVO.")
        if isinstance(valor, str):
            raise ValueError("EL IDENTIFICADOR DE LA CATEGORÍA DEBE SER UN NÚMERO ENTERO POSITIVO.")
        return valor


# DTO PARA ACTUALIZAR UN PRODUCTO (HEREDA LAS VALIDACIONES DE REGISTRO)
class ProductoActualizar(ProductoRegistro):
    pass
