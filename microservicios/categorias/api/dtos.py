
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


# DTO PARA REGISTRAR UNA CATEGORÍA
class CategoriaRegistro(BaseModel):

    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=5, max_length=250)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s]+", valor):
            raise ValueError("EL NOMBRE DE LA CATEGORÍA SOLO DEBE CONTENER LETRAS, NÚMEROS Y ESPACIOS.")
        return valor

    @field_validator("descripcion")
    @classmethod
    def ValidarDescripcion(cls, valor):
        if not valor.strip():
            raise ValueError("LA DESCRIPCIÓN ES OBLIGATORIA.")
        return valor


# DTO PARA ACTUALIZAR UNA CATEGORÍA
class CategoriaActualizar(BaseModel):

    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=5, max_length=250)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s]+", valor):
            raise ValueError("EL NOMBRE DE LA CATEGORÍA SOLO DEBE CONTENER LETRAS, NÚMEROS Y ESPACIOS.")
        return valor

    @field_validator("descripcion")
    @classmethod
    def ValidarDescripcion(cls, valor):
        if not valor.strip():
            raise ValueError("LA DESCRIPCIÓN ES OBLIGATORIA.")
        return valor
