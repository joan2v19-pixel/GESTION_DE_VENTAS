
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
import re


# DTO PARA REGISTRAR PROVEEDORES
class ProveedorRegistro(BaseModel):

    identificacion: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="NÚMERO DE IDENTIFICACIÓN ÚNICO DEL PROVEEDOR (SOLO DÍGITOS, ENTRE 5 Y 20 CARACTERES).",
        examples=["900123456"]
    )
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="NOMBRE O RAZÓN SOCIAL DEL PROVEEDOR (ENTRE 3 Y 100 CARACTERES).",
        examples=["Distribuidora ABC S.A.S."]
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=15,
        description="TELÉFONO DE CONTACTO DEL PROVEEDOR (SOLO DÍGITOS, ENTRE 7 Y 15 CARACTERES).",
        examples=["3001234567"]
    )
    correo: EmailStr = Field(
        ...,
        description="CORREO ELECTRÓNICO VÁLIDO DEL PROVEEDOR.",
        examples=["contacto@distribuidoraabc.com"]
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=150,
        description="DIRECCIÓN FÍSICA O COMERCIAL DEL PROVEEDOR (ENTRE 5 Y 150 CARACTERES).",
        examples=["Calle 10 # 20-30"]
    )

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

    # VALIDAR EL NOMBRE O RAZON SOCIAL
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s.,&'()\-]+", valor):
            raise ValueError("EL NOMBRE CONTIENE CARACTERES NO PERMITIDOS.")
        return valor

    # VALIDAR QUE EL TELEFONO CONTENGA SOLO NUMEROS
    @field_validator("telefono")
    @classmethod
    def ValidarTelefono(cls, valor):
        if not valor.isdigit():
            raise ValueError("EL TELÉFONO DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE LA DIRECCION NO CONTENGA SOLO ESPACIOS
    @field_validator("direccion")
    @classmethod
    def ValidarDireccion(cls, valor):
        if not valor.strip():
            raise ValueError("LA DIRECCIÓN ES OBLIGATORIA.")
        return valor


# DTO PARA ACTUALIZAR PROVEEDORES
class ProveedorActualizar(BaseModel):

    identificacion: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="NÚMERO DE IDENTIFICACIÓN ÚNICO DEL PROVEEDOR (SOLO DÍGITOS, ENTRE 5 Y 20 CARACTERES).",
        examples=["900123456"]
    )
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="NOMBRE O RAZÓN SOCIAL DEL PROVEEDOR (ENTRE 3 Y 100 CARACTERES).",
        examples=["Proveedor actualizado"]
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=15,
        description="TELÉFONO DE CONTACTO DEL PROVEEDOR (SOLO DÍGITOS, ENTRE 7 Y 15 CARACTERES).",
        examples=["3009876543"]
    )
    correo: EmailStr = Field(
        ...,
        description="CORREO ELECTRÓNICO VÁLIDO DEL PROVEEDOR.",
        examples=["contacto@proveedor.com"]
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=150,
        description="DIRECCIÓN FÍSICA O COMERCIAL DEL PROVEEDOR (ENTRE 5 Y 150 CARACTERES).",
        examples=["Calle 10 # 20-30"]
    )

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

    # VALIDAR EL NOMBRE O RAZON SOCIAL
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s.,&'()\-]+", valor):
            raise ValueError("EL NOMBRE CONTIENE CARACTERES NO PERMITIDOS.")
        return valor

    # VALIDAR QUE EL TELEFONO CONTENGA SOLO NUMEROS
    @field_validator("telefono")
    @classmethod
    def ValidarTelefono(cls, valor):
        if not valor.isdigit():
            raise ValueError("EL TELÉFONO DEBE CONTENER SOLO NÚMEROS.")
        return valor

    # VALIDAR QUE LA DIRECCION NO CONTENGA SOLO ESPACIOS
    @field_validator("direccion")
    @classmethod
    def ValidarDireccion(cls, valor):
        if not valor.strip():
            raise ValueError("LA DIRECCIÓN ES OBLIGATORIA.")
        return valor
