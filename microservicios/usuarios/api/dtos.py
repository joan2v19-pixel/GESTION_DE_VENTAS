
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


# DTO PARA REGISTRAR USUARIOS
class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombreUsuario: str = Field(..., min_length=3, max_length=30)
    contrasena: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    # VALIDAR QUE EL NOMBRE SOLO CONTENGA LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE LA IDENTIFICACION SOLO CONTENGA NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN SOLO DEBE CONTENER NÚMEROS.")
        return valor

    # VALIDAR EL NOMBRE DE USUARIO
    @field_validator("nombreUsuario")
    @classmethod
    def ValidarNombreUsuario(cls, valor):
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", valor):
            raise ValueError(
                "EL NOMBRE DE USUARIO SOLO PUEDE CONTENER LETRAS, NÚMEROS, PUNTO, GUION Y GUION BAJO."
            )
        return valor

    # VALIDAR LA SEGURIDAD DE LA CONTRASEÑA
    @field_validator("contrasena")
    @classmethod
    def ValidarContrasena(cls, valor):
        if not re.search(r"[A-Z]", valor):
            raise ValueError("LA CONTRASEÑA DEBE CONTENER UNA MAYÚSCULA.")

        if not re.search(r"[a-z]", valor):
            raise ValueError("LA CONTRASEÑA DEBE CONTENER UNA MINÚSCULA.")

        if not re.search(r"[0-9]", valor):
            raise ValueError("LA CONTRASEÑA DEBE CONTENER UN NÚMERO.")

        if not re.search(r"[^a-zA-Z0-9]", valor):
            raise ValueError("LA CONTRASEÑA DEBE CONTENER UN CARÁCTER ESPECIAL.")

        return valor


# DTO PARA ACTUALIZAR USUARIOS
class UsuarioActualizar(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombreUsuario: str = Field(..., min_length=3, max_length=30)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    # VALIDAR QUE EL NOMBRE SOLO CONTENGA LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE LA IDENTIFICACION SOLO CONTENGA NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN SOLO DEBE CONTENER NÚMEROS.")
        return valor

    # VALIDAR EL NOMBRE DE USUARIO
    @field_validator("nombreUsuario")
    @classmethod
    def ValidarNombreUsuario(cls, valor):
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", valor):
            raise ValueError(
                "EL NOMBRE DE USUARIO SOLO PUEDE CONTENER LETRAS, NÚMEROS, PUNTO, GUION Y GUION BAJO."
            )
        return valor


# DTO PARA INICIAR SESION
class UsuarioLogin(BaseModel):
    nombreUsuario: str = Field(..., min_length=3, max_length=30)
    contrasena: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
