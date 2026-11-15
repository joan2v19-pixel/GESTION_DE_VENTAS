
from pydantic import BaseModel, Field, ConfigDict


# DTO para registrar usuarios
class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombreUsuario: str = Field(..., min_length=3, max_length=30)
    contrasena: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )


# DTO para actualizar usuarios
class UsuarioActualizar(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombreUsuario: str = Field(..., min_length=3, max_length=30)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )


# DTO para iniciar sesión
class UsuarioLogin(BaseModel):
    nombreUsuario: str = Field(..., min_length=3, max_length=30)
    contrasena: str = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
