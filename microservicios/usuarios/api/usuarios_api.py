from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from microservicios.usuarios.dominio.usuario import (
    Usuario,
    registrar_usuario
)

router = APIRouter(
    prefix="/api/Usuarios",
    tags=["Gestión de usuarios"]
)


class RespuestaUsuario(BaseModel):
    mensaje: str
    data: dict | None
    success: bool


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RespuestaUsuario
)
def crear_usuario(usuario: Usuario):

    try:
        nuevo_usuario = registrar_usuario(usuario)

        # Excluir la contraseña de la respuesta
        usuario_respuesta = {
            "id": nuevo_usuario["id"],
            "nombre": nuevo_usuario["nombre"],
            "identificacion": nuevo_usuario["identificacion"],
            "nombreUsuario": nuevo_usuario["nombreUsuario"]
        }

        return {
            "mensaje": "Usuario registrado correctamente",
            "data": usuario_respuesta,
            "success": True
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )