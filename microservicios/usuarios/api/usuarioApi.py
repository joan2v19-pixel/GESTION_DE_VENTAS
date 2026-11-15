from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from microservicios.usuarios.servicio import usuarioServicio


router = APIRouter(
    prefix="/api/Usuarios",
    tags=["Gestión de usuarios"]
)


# Modelo para registrar usuarios
class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombreUsuario: str = Field(..., min_length=3, max_length=30)
    contrasena: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )


# Modelo para actualizar usuarios
class UsuarioActualizar(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    identificacion: str = Field(..., min_length=5, max_length=20)
    nombreUsuario: str = Field(..., min_length=3, max_length=30)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )


# Modelo para iniciar sesión
class UsuarioLogin(BaseModel):
    nombreUsuario: str = Field(..., min_length=3, max_length=30)
    contrasena: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )


# Endpoint para registrar usuarios
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarUsuarioAPI(usuario: UsuarioRegistro):

    try:
        nuevo_usuario = usuarioServicio.RegistrarUsuarioServicio(
            usuario.model_dump()
        )

        return {
            "mensaje": "Usuario registrado correctamente",
            "data": {
                "id": nuevo_usuario["id"],
                "nombre": nuevo_usuario["nombre"],
                "identificacion": nuevo_usuario["identificacion"],
                "nombreUsuario": nuevo_usuario["nombreUsuario"]
            },
            "success": True
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


# Endpoint para actualizar usuarios
@router.put("/{id_usuario}")
def ActualizarUsuarioAPI(
    id_usuario: int,
    datos: UsuarioActualizar
):

    try:
        usuario_actualizado = usuarioServicio.ActualizarUsuarioServicio(
            id_usuario,
            datos.model_dump()
        )

        return {
            "mensaje": "La información del usuario se actualizó correctamente.",
            "usuario": {
                "id": usuario_actualizado["id"],
                "nombre": usuario_actualizado["nombre"],
                "identificacion": usuario_actualizado["identificacion"],
                "nombreUsuario": usuario_actualizado["nombreUsuario"]
            }
        }

    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario solicitado."
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

# Endpoint para consultar todos los usuarios
@router.get("/")
def ConsultarUsuariosAPI():

    try:
        usuarios = usuarioServicio.ConsultarUsuariosServicio()

        return usuarios

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible consultar los usuarios."
        )


# Endpoint para iniciar sesión
@router.post("/login")
def IniciarSesionAPI(datos: UsuarioLogin):

    try:
        usuario = usuarioServicio.IniciarSesionServicio(
            datos.nombreUsuario,
            datos.contrasena
        )

        return {
            "mensaje": "Inicio de sesión exitoso",
            "success": True,
            "data": usuario
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible completar la autenticación"
        )


