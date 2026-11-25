
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
import re


# DTO PARA REGISTRAR CLIENTES
class ClienteRegistro(BaseModel):

    identificacion: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=15)
    correo: EmailStr

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    # VALIDAR QUE LA IDENTIFICACION CONTENGA SOLO NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE EL NOMBRE CONTENGA SOLO LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE EL TELEFONO CONTENGA SOLO NUMEROS
    @field_validator("telefono")
    @classmethod
    def ValidarTelefono(cls, valor):
        if not valor.isdigit():
            raise ValueError("EL TELÉFONO DEBE CONTENER SOLO NÚMEROS.")
        return valor


# DTO PARA ACTUALIZAR CLIENTES
class ClienteActualizar(BaseModel):

    identificacion: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=15)
    correo: EmailStr

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    # VALIDAR QUE LA IDENTIFICACION CONTENGA SOLO NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE EL NOMBRE CONTENGA SOLO LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE EL TELEFONO CONTENGA SOLO NUMEROS
    @field_validator("telefono")
    @classmethod
    def ValidarTelefono(cls, valor):
        if not valor.isdigit():
            raise ValueError("EL TELÉFONO DEBE CONTENER SOLO NÚMEROS.")
        return valor
