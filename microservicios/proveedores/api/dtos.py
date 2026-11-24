
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ProveedorRegistro(BaseModel):
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=3, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=15)
    correo: EmailStr
    direccion: str = Field(..., min_length=5, max_length=150)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
