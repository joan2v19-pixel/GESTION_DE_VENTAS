
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


# DTO PARA REGISTRAR UNA CATEGORÍA
class CategoriaRegistro(BaseModel):

    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="NOMBRE ÚNICO DE LA CATEGORÍA (LETRAS, NÚMEROS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES).",
        examples=["Accesorios"]
    )
    descripcion: str = Field(
        ...,
        min_length=5,
        max_length=250,
        description="DESCRIPCIÓN DETALLADA DE LA CATEGORÍA (ENTRE 5 Y 250 CARACTERES).",
        examples=["Categoría para productos accesorios"]
    )

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

    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="NOMBRE ÚNICO DE LA CATEGORÍA (LETRAS, NÚMEROS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES).",
        examples=["Bebidas"]
    )
    descripcion: str = Field(
        ...,
        min_length=5,
        max_length=250,
        description="DESCRIPCIÓN DETALLADA DE LA CATEGORÍA (ENTRE 5 Y 250 CARACTERES).",
        examples=["Productos líquidos para consumo"]
    )

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
