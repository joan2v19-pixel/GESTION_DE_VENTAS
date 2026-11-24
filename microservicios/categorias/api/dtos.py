
from pydantic import BaseModel, Field, ConfigDict


# DTO para registrar una categoría
class CategoriaRegistro(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=5, max_length=250)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )
