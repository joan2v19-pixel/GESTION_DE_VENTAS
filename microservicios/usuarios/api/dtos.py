
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
import re


def _EsValorPorDefecto(valor: str) -> bool:
    return valor.strip().lower() == "string"


# DTO PARA REGISTRAR USUARIOS
class UsuarioRegistro(BaseModel):
    nombre: str = Field(
        default="string",
        min_length=3,
        max_length=100,
        description="NOMBRE COMPLETO DEL USUARIO (SOLO LETRAS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES)."
    )
    identificacion: str = Field(
        default="string",
        min_length=5,
        max_length=20,
        description="NÚMERO DE IDENTIFICACIÓN ÚNICO DEL USUARIO (SOLO DÍGITOS, ENTRE 5 Y 20 CARACTERES)."
    )
    nombreUsuario: str = Field(
        default="string",
        min_length=3,
        max_length=30,
        description="NOMBRE DE USUARIO ÚNICO PARA INICIAR SESIÓN (LETRAS, NÚMEROS, PUNTO, GUION Y GUION BAJO)."
    )
    contrasena: str = Field(
        default="string",
        min_length=8,
        max_length=100,
        description="CONTRASEÑA DE ACCESO (MÍNIMO 8 CARACTERES, CON MAYÚSCULA, MINÚSCULA, NÚMERO Y CARÁCTER ESPECIAL)."
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True
    )

    # VALIDAR QUE EL NOMBRE SOLO CONTENGA LETRAS Y ESPACIOS
    @field_validator("nombre")
    @classmethod
    def ValidarNombre(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("EL NOMBRE NO PUEDE SER 'string'.")
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", valor):
            raise ValueError("EL NOMBRE SOLO DEBE CONTENER LETRAS Y ESPACIOS.")
        return valor

    # VALIDAR QUE LA IDENTIFICACION SOLO CONTENGA NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if _EsValorPorDefecto(valor) or not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN SOLO DEBE CONTENER NÚMEROS.")
        return valor

    # VALIDAR EL NOMBRE DE USUARIO
    @field_validator("nombreUsuario")
    @classmethod
    def ValidarNombreUsuario(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("EL NOMBRE DE USUARIO NO PUEDE SER 'string'.")
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", valor):
            raise ValueError(
                "EL NOMBRE DE USUARIO SOLO PUEDE CONTENER LETRAS, NÚMEROS, PUNTO, GUION Y GUION BAJO."
            )
        return valor

    # VALIDAR LA SEGURIDAD DE LA CONTRASEÑA
    @field_validator("contrasena")
    @classmethod
    def ValidarContrasena(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("LA CONTRASEÑA NO PUEDE SER 'string'.")
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
    nombre: str = Field(
        default="string",
        description="NOMBRE COMPLETO DEL USUARIO (SOLO LETRAS Y ESPACIOS, ENTRE 3 Y 100 CARACTERES)."
    )
    identificacion: str = Field(
        default="string",
        description="NÚMERO DE IDENTIFICACIÓN ÚNICO DEL USUARIO (SOLO DÍGITOS, ENTRE 5 Y 20 CARACTERES)."
    )
    nombreUsuario: str = Field(
        default="string",
        description="NOMBRE DE USUARIO ÚNICO PARA INICIAR SESIÓN (LETRAS, NÚMEROS, PUNTO, GUION Y GUION BAJO)."
    )
    estado: bool = Field(
        default=True,
        description=(
            "ESTADO DE LA CUENTA: TRUE PARA ACTIVA Y FALSE PARA INACTIVA. "
            "SI SE OMITE, SE CONSERVA EL ESTADO ACTUAL."
        ),
        examples=[True]
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True
    )

    # VALIDAR QUE EL NOMBRE SOLO CONTENGA LETRAS Y ESPACIOS
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

    # VALIDAR QUE LA IDENTIFICACION SOLO CONTENGA NUMEROS
    @field_validator("identificacion")
    @classmethod
    def ValidarIdentificacion(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if len(valor) < 5 or len(valor) > 20:
            raise ValueError("LA IDENTIFICACIÓN DEBE TENER ENTRE 5 Y 20 CARACTERES.")
        if not valor.isdigit():
            raise ValueError("LA IDENTIFICACIÓN SOLO DEBE CONTENER NÚMEROS.")
        return valor

    # VALIDAR EL NOMBRE DE USUARIO
    @field_validator("nombreUsuario")
    @classmethod
    def ValidarNombreUsuario(cls, valor):
        if _EsValorPorDefecto(valor):
            return "string"
        if len(valor) < 3 or len(valor) > 30:
            raise ValueError("EL NOMBRE DE USUARIO DEBE TENER ENTRE 3 Y 30 CARACTERES.")
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", valor):
            raise ValueError(
                "EL NOMBRE DE USUARIO SOLO PUEDE CONTENER LETRAS, NÚMEROS, PUNTO, GUION Y GUION BAJO."
            )
        return valor

    @model_validator(mode="after")
    def ValidarAlMenosUnCampo(self):
        if (
            _EsValorPorDefecto(self.nombre)
            and _EsValorPorDefecto(self.identificacion)
            and _EsValorPorDefecto(self.nombreUsuario)
            and "estado" not in self.model_fields_set
        ):
            raise ValueError("DEBE ENVIAR AL MENOS UN CAMPO VÁLIDO PARA ACTUALIZAR.")
        return self


# DTO PARA INICIAR SESION
class UsuarioLogin(BaseModel):
    nombreUsuario: str = Field(
        default="string",
        min_length=3,
        max_length=30,
        description="NOMBRE DE USUARIO REGISTRADO EN EL SISTEMA."
    )
    contrasena: str = Field(
        default="string",
        min_length=8,
        max_length=100,
        description="CONTRASEÑA DE ACCESO DEL USUARIO."
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True
    )

    @field_validator("nombreUsuario")
    @classmethod
    def ValidarNombreUsuario(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("EL NOMBRE DE USUARIO NO PUEDE SER 'string'.")
        return valor

    @field_validator("contrasena")
    @classmethod
    def ValidarContrasena(cls, valor):
        if _EsValorPorDefecto(valor):
            raise ValueError("LA CONTRASEÑA NO PUEDE SER 'string'.")
        return valor


# DTO PARA CONSULTAR USUARIOS REGISTRADOS (SIN CONTRASEÑA NI DATOS SENSIBLES)
class UsuarioConsulta(BaseModel):
    id: int = Field(..., description="IDENTIFICADOR ÚNICO DEL USUARIO.", examples=[1])
    nombre: str = Field(..., description="NOMBRE COMPLETO DEL USUARIO.", examples=["Joan Sierra"])
    identificacion: str = Field(..., description="NÚMERO DE IDENTIFICACIÓN DEL USUARIO.", examples=["1234567890"])
    nombreUsuario: str = Field(..., description="NOMBRE DE USUARIO PARA INICIAR SESIÓN.", examples=["Joan"])
    estado: bool = Field(..., description="INDICA SI LA CUENTA ESTÁ ACTIVA.", examples=[True])
