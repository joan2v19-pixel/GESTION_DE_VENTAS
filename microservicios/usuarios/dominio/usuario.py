from pydantic import BaseModel, Field, ConfigDict


class Usuario(BaseModel):
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nombre completo del usuario"
    )

    identificacion: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Identificación única del usuario"
    )

    nombreUsuario: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Nombre de usuario para ingresar al sistema"
    )

    contrasena: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña de acceso"
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

from pwdlib import PasswordHash
from microservicios.usuarios.repositorio import usuarios_repositorio

# Instancia para proteger contraseñas con Argon2
password_hash = PasswordHash.recommended()


def registrar_usuario(usuario: Usuario):

    # Verificar identificación duplicada
    if usuarios_repositorio.existe_identificacion(
        usuario.identificacion
    ):
        raise ValueError("La identificación ya está registrada")

    # Verificar nombre de usuario duplicado
    if usuarios_repositorio.existe_nombre_usuario(
        usuario.nombreUsuario
    ):
        raise ValueError("El nombre de usuario ya existe")

    # Generar hash de la contraseña
    contrasena_hash = password_hash.hash(usuario.contrasena)

    # Preparar información para almacenar
    nuevo_usuario = {
        "nombre": usuario.nombre,
        "identificacion": usuario.identificacion,
        "nombreUsuario": usuario.nombreUsuario,
        "contrasena": contrasena_hash
    }

    # Guardar en el repositorio
    return usuarios_repositorio.guardar(nuevo_usuario)