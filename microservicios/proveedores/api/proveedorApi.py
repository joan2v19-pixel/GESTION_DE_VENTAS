
from fastapi import APIRouter, HTTPException, status, Depends

from microservicios.usuarios.api.usuarioApi import ObtenerUsuarioAutenticado
from microservicios.proveedores.api.dtos import ProveedorRegistro, ProveedorActualizar
from microservicios.proveedores.servicio import proveedorServicio


router = APIRouter(
    prefix="/api/v1/proveedores",
    tags=["Gestión de proveedores"]
)


# Registrar un proveedor
@router.post("/", status_code=status.HTTP_201_CREATED)
def RegistrarProveedorAPI(
    datos: ProveedorRegistro,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        proveedor = proveedorServicio.RegistrarProveedorServicio(
            datos.model_dump()
        )

        return {
            "mensaje": "PROVEEDOR REGISTRADO EXITOSAMENTE.",
            "data": proveedor,
            "success": True
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE REGISTRAR EL PROVEEDOR."
        )


# Consultar todos los proveedores
@router.get("/", status_code=status.HTTP_200_OK)
def ConsultarProveedoresAPI(
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        proveedores = proveedorServicio.ConsultarProveedoresServicio()

        if not proveedores:
            return {
                "mensaje": "NO EXISTEN PROVEEDORES REGISTRADOS.",
                "data": [],
                "success": True
            }

        return {
            "mensaje": "CONSULTA DE PROVEEDORES EXITOSA.",
            "data": proveedores,
            "success": True
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR LOS PROVEEDORES."
        )



# Buscar proveedores por diferentes criterios
@router.get("/buscar", status_code=status.HTTP_200_OK)
def BuscarProveedoresAPI(
    nombre: str | None = None,
    identificacion: str | None = None,
    telefono: str | None = None,
    correo: str | None = None,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        # Limpiar los criterios ingresados
        nombre = nombre.strip() if nombre else None
        identificacion = identificacion.strip() if identificacion else None
        telefono = telefono.strip() if telefono else None
        correo = correo.strip() if correo else None

        # Validar que exista al menos un criterio
        if not any([nombre, identificacion, telefono, correo]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DEBE INGRESAR AL MENOS UN CRITERIO DE BÚSQUEDA."
            )

        proveedores = proveedorServicio.BuscarProveedoresServicio(
            nombre,
            identificacion,
            telefono,
            correo
        )

        if not proveedores:
            return {
                "mensaje": "NO SE ENCONTRARON PROVEEDORES CON LOS CRITERIOS INGRESADOS.",
                "data": [],
                "success": True
            }

        return {
            "mensaje": "BÚSQUEDA DE PROVEEDORES EXITOSA.",
            "data": proveedores,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE REALIZAR LA BÚSQUEDA DE PROVEEDORES."
        )


# Consultar un proveedor por ID
@router.get("/{id}", status_code=status.HTTP_200_OK)
def ObtenerProveedorPorIdAPI(
    id: int,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        proveedor = proveedorServicio.ObtenerProveedorPorIdServicio(id)

        if proveedor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO."
            )

        return {
            "mensaje": "PROVEEDOR CONSULTADO EXITOSAMENTE.",
            "data": proveedor,
            "success": True
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE CONSULTAR EL PROVEEDOR."
        )



# Actualizar un proveedor
@router.put("/{id}", status_code=status.HTTP_200_OK)
def ActualizarProveedorAPI(
    id: int,
    datos: ProveedorActualizar,
    usuario_autenticado: dict = Depends(ObtenerUsuarioAutenticado)
):
    try:
        proveedor = proveedorServicio.ActualizarProveedorServicio(
            id,
            datos.model_dump()
        )

        return {
            "mensaje": "PROVEEDOR ACTUALIZADO EXITOSAMENTE.",
            "data": proveedor,
            "success": True
        }

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NO FUE POSIBLE ACTUALIZAR EL PROVEEDOR."
        )


