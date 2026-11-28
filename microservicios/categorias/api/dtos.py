
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
import re


def _EsValorPorDefecto(valor: str) -> bool:
    return valor.strip().lower() == "string"


# DTO PARA REGISTRAR UNA CATEGORÍA
class CategoriaRegistro(BaseModel):

    nombre: str = Field(
        default="string",
        min_length=3,
        max_length=100,
        description="NOMBRE ÚNICO DE LA CATEGORÍA (LETRAS, NÚMEROS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES)."
    )
    descripcion: str = Field(
        default="string",
        min_length=5,
        max_length=250,
        description="DESCRIPCIÓN DETALLADA DE LA CATEGORÍA (ENTRE 5 Y 250 CARACTERES)."
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True
    )

    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("EL NOMBRE DE LA CATEGORÍA NO PUEDE SER 'string'.")
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s]+", valor):
            raise ValueError("EL NOMBRE DE LA CATEGORÍA SOLO DEBE CONTENER LETRAS, NÚMEROS Y ESPACIOS.")
        return valor

    @field_validator("descripcion")
    @classmethod
    def ValidarDescripcion(cls, valor):
        if not valor.strip():
            raise ValueError("LA DESCRIPCIÓN ES OBLIGATORIA.")
        if _EsValorPorDefecto(valor):
            raise ValueError("LA DESCRIPCIÓN DE LA CATEGORÍA NO PUEDE SER 'string'.")
        return valor


# DTO PARA ACTUALIZAR UNA CATEGORÍA
class CategoriaActualizar(BaseModel):

    nombre: str = Field(
        default="string",
        description="NOMBRE ÚNICO DE LA CATEGORÍA (LETRAS, NÚMEROS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES)."
    )
    descripcion: str = Field(
        default="string",
        description="DESCRIPCIÓN DETALLADA DE LA CATEGORÍA (ENTRE 5 Y 250 CARACTERES)."
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if len(valor) < 3 or len(valor) > 100:
            raise ValueError("EL NOMBRE DE LA CATEGORÍA DEBE TENER ENTRE 3 Y 100 CARACTERES.")
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s]+", valor):
            raise ValueError("EL NOMBRE DE LA CATEGORÍA SOLO DEBE CONTENER LETRAS, NÚMEROS Y ESPACIOS.")
        return valor

    @field_validator("descripcion")
    @classmethod
    def ValidarDescripcion(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if not valor.strip():
            raise ValueError("LA DESCRIPCIÓN ES OBLIGATORIA.")
        if len(valor) < 5 or len(valor) > 250:
            raise ValueError("LA DESCRIPCIÓN DE LA CATEGORÍA DEBE TENER ENTRE 5 Y 250 CARACTERES.")
        return valor

    @model_validator(mode="after")
    def ValidarAlMenosUnCampo(self):
        if _EsValorPorDefecto(self.nombre) and _EsValorPorDefecto(self.descripcion):
            raise ValueError("DEBE ENVIAR AL MENOS UN CAMPO VÁLIDO DIFERENTE DE 'string' PARA ACTUALIZAR.")
        return self
