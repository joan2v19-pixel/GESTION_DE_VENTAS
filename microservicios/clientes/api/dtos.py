
from pydantic import BaseModel, Field, ConfigDict, EmailStr, TypeAdapter, field_validator, model_validator
import re


_VALIDADOR_EMAIL = TypeAdapter(EmailStr)


def _EsValorPorDefecto(valor: str) -> bool:
    return valor.strip().lower() == "string"


# DTO PARA REGISTRAR CLIENTES
class ClienteRegistro(BaseModel):

    identificacion: str = Field(
        default="string",
        min_length=5,
        max_length=20,
        description="NÚMERO DE IDENTIFICACIÓN ÚNICO DEL CLIENTE (SOLO DÍGITOS, ENTRE 5 Y 20 CARACTERES)."
    )
    nombre: str = Field(
        default="string",
        min_length=3,
        max_length=100,
        description="NOMBRE COMPLETO DEL CLIENTE (SOLO LETRAS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES)."
    )
    telefono: str = Field(
        default="string",
        min_length=7,
        max_length=15,
        description="TELÉFONO DE CONTACTO DEL CLIENTE (SOLO DÍGITOS, ENTRE 7 Y 15 CARACTERES)."
    )
    correo: EmailStr = Field(
        default="string",
        description="CORREO ELECTRÓNICO VÁLIDO DEL CLIENTE."
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True
    )

    # VALIDAR QUE LA IDENTIFICACION CONTENGA SOLO NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if _EsValorPorDefecto(valor) or not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE EL NOMBRE CONTENGA SOLO LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("EL NOMBRE NO PUEDE SER 'string'.")
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE EL TELEFONO CONTENGA SOLO NUMEROS
    @field_validator("telefono")
    @classmethod
    def ValidarTelefono(cls, valor):
        if _EsValorPorDefecto(valor) or not valor.isdigit():
            raise ValueError("EL TELÉFONO DEBE CONTENER SOLO NÚMEROS.")
        return valor


# DTO PARA ACTUALIZAR CLIENTES
class ClienteActualizar(BaseModel):

    identificacion: str = Field(
        default="string",
        description="NÚMERO DE IDENTIFICACIÓN ÚNICO DEL CLIENTE (SOLO DÍGITOS, ENTRE 5 Y 20 CARACTERES)."
    )
    nombre: str = Field(
        default="string",
        description="NOMBRE COMPLETO DEL CLIENTE (SOLO LETRAS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES)."
    )
    telefono: str = Field(
        default="string",
        description="TELÉFONO DE CONTACTO DEL CLIENTE (SOLO DÍGITOS, ENTRE 7 Y 15 CARACTERES)."
    )
    correo: str = Field(
        default="string",
        description="CORREO ELECTRÓNICO VÁLIDO DEL CLIENTE."
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True
    )

    # VALIDAR QUE LA IDENTIFICACION CONTENGA SOLO NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if len(valor) < 5 or len(valor) > 20:
            raise ValueError("LA IDENTIFICACIÓN DEBE TENER ENTRE 5 Y 20 CARACTERES.")
        if not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE EL NOMBRE CONTENGA SOLO LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if len(valor) < 3 or len(valor) > 100:
            raise ValueError("EL NOMBRE DEBE TENER ENTRE 3 Y 100 CARACTERES.")
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE EL TELEFONO CONTENGA SOLO NUMEROS
    @field_validator("telefono")
    @classmethod
    def ValidarTelefono(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if len(valor) < 7 or len(valor) > 15:
            raise ValueError("EL TELÉFONO DEBE TENER ENTRE 7 Y 15 CARACTERES.")
        if not valor.isdigit():
            raise ValueError("EL TELÉFONO DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE EL CORREO SEA VÁLIDO SI NO ES 'string'
    @field_validator("correo")
    @classmethod
    def ValidarCorreo(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        return str(_VALIDADOR_EMAIL.validate_python(valor))

    @model_validator(mode="after")
    def ValidarAlMenosUnCampo(self):
        if (
            _EsValorPorDefecto(self.identificacion)
            and _EsValorPorDefecto(self.nombre)
            and _EsValorPorDefecto(self.telefono)
            and _EsValorPorDefecto(self.correo)
        ):
            raise ValueError("DEBE ENVIAR AL MENOS UN CAMPO VÁLIDO DIFERENTE DE 'string' PARA ACTUALIZAR.")
        return self
