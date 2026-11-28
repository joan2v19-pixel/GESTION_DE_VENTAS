from fastapi import APIRouter, Path, Query, status, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
import re

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.productos.api.dtos import (
    PALABRAS_PROHIBIDAS,
    ProductoActualizar,
    ProductoRegistro
)
from microservicios.productos.servicio import productoServicio


class RutaValidacionProducto(APIRoute):
    """Devuelve errores de validación de productos en español y con formato JSON estable."""

    def get_route_handler(self):
        manejador_original = super().get_route_handler()

        async def manejar_validacion(request):
            try:
                return await manejador_original(request)
            except RequestValidationError as error:
                etiquetas = {
                    "nombre": "nombre",
                    "codigo": "código",
                    "precio": "precio",
                    "categoria_id": "categoría",
                    "id": "identificador"
                }
                detalles = []
                campos_faltantes = []

                for detalle in error.errors():
                    ubicacion = detalle.get("loc", ())
                    campo = str(ubicacion[-1]) if ubicacion else "dato"
                    etiqueta = etiquetas.get(campo, campo.replace("_", " "))
                    tipo = detalle.get("type", "")
                    minimo = detalle.get("ctx", {}).get("min_length")

                    if tipo == "missing":
                        campos_faltantes.append(etiqueta)
                        mensaje = f"Debe completar el campo {etiqueta}."
                    elif tipo == "string_too_short":
                        mensaje = f"El campo {etiqueta} debe tener al menos {minimo} caracteres."
                    elif tipo == "string_too_long":
                        maximo = detalle.get("ctx", {}).get("max_length")
                        mensaje = f"El campo {etiqueta} no puede superar {maximo} caracteres."
                    elif tipo in {"float_parsing", "int_parsing", "int_type", "float_type"}:
                        mensaje = f"El campo {etiqueta} debe tener un valor numérico válido."
                    elif tipo == "greater_than":
                        mensaje = f"El campo {etiqueta} debe ser mayor que cero."
                    elif tipo == "extra_forbidden":
                        mensaje = f"El campo {etiqueta} no está permitido."
                    else:
                        mensaje = detalle.get("msg", f"El campo {etiqueta} no es válido.")
                        if mensaje.lower().startswith("value error, "):
                            mensaje = mensaje[len("value error, "):]

                    detalles.append({"campo": etiqueta, "mensaje": mensaje})

                if campos_faltantes:
                    faltantes = ", ".join(dict.fromkeys(campos_faltantes))
                    resumen = f"Faltan campos obligatorios: {faltantes}."
                else:
                    resumen = "Los datos ingresados no son válidos. Verifique los campos indicados."

                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "message": resumen,
                        "success": False,
                        "data": None
                    }
                )

        return manejar_validacion


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE PRODUCTOS
router = APIRouter(
    prefix="/api/v1/productos",
    tags=["Gestión de productos"],
    route_class=RutaValidacionProducto
)


# 1. CONSULTAR TODOS LOS PRODUCTOS REGISTRADOS
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar todos los productos",
    description=(
        "Obtiene el listado completo de productos registrados en el sistema con su "
        "identificador, nombre, código, precio y categoría asociada. Si no existen "
        "registros, retorna una lista vacía."
    ),
    responses={
        200: {
            "description": "Consulta de productos exitosa o sin registros",
            "content": {
                "application/json": {
                    "examples": {
                        "con_registros": {
                            "summary": "Productos encontrados",
                            "value": {
                                "message": "Consulta de productos exitosa",
                                "data": [
                                    {
                                        "id": 1,
                                        "nombre": "Arroz",
                                        "codigo": "PROD-001",
                                        "precio": 3500.0,
                                        "categoria_id": 1,
                                        "categoria": "Granos"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_registros": {
                            "summary": "Sin productos registrados",
                            "value": {
                                "message": "No existen productos registrados",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar los productos",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible consultar los productos",
                        "data": [],
                        "success": False
                    }
                }
            }
        }
    }
)
def ConsultarProductosAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # CONSULTAR LOS PRODUCTOS DESDE EL SERVICIO
        productos = productoServicio.ConsultarProductosServicio()

        if not productos:
            return {
                "message": "No existen productos registrados",
                "data": [],
                "success": True
            }

        return {
            "message": "Consulta de productos exitosa",
            "data": productos,
            "success": True
        }

    except Exception:
        # RETORNAR ERROR CONTROLADO SI FALLA LA CONSULTA
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar los productos",
                "data": [],
                "success": False
            }
        )


# 2. REGISTRAR UN NUEVO PRODUCTO
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo producto",
    description=(
        "Registra un nuevo producto en el catálogo validando los campos obligatorios, "
        "que el precio sea un valor numérico mayor a cero, que el código no esté duplicado "
        "y que la categoría asociada exista en el sistema."
    ),
    responses={
        201: {
            "description": "Producto registrado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Producto registrado correctamente",
                        "data": {
                            "id": 1,
                            "nombre": "Arroz",
                            "codigo": "PROD-001",
                            "precio": 3500.0,
                            "categoria_id": 1
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "La categoría seleccionada no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "La categoría seleccionada no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "El código del producto ya se encuentra registrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El código del producto ya se encuentra registrado",
                        "success": False
                    }
                }
            }
        },
        422: {
            "description": "Datos obligatorios incompletos o inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "campo_vacio": {
                            "summary": "Campo nombre vacío",
                            "value": {
                                "message": "Los datos ingresados no son válidos. Verifique los campos indicados.",
                                "success": False,
                                "errors": [
                                    {
                                        "campo": "nombre",
                                        "mensaje": "El campo nombre debe tener al menos 2 caracteres."
                                    }
                                ]
                            }
                        },
                        "campo_faltante": {
                            "summary": "Falta un campo obligatorio",
                            "value": {
                                "message": "Faltan campos obligatorios: nombre.",
                                "success": False,
                                "errors": [
                                    {
                                        "campo": "nombre",
                                        "mensaje": "Debe completar el campo nombre."
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al intentar guardar el producto",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar el producto",
                        "success": False
                    }
                }
            }
        }
    }
)
def RegistrarProductoAPI(
    datos: ProductoRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # INVOCAR EL SERVICIO PARA REGISTRAR EL PRODUCTO
        producto = productoServicio.RegistrarProductoServicio(
            datos.model_dump()
        )

        # RETORNAR RESPUESTA DE REGISTRO EXITOSO
        return {
            "message": "Producto registrado correctamente",
            "data": producto,
            "success": True
        }

    except ValueError as error:
        # RETORNAR CONFLICTO SI EL CÓDIGO DEL PRODUCTO YA EXISTE
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "data": None,
                "success": False
            }
        )

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI LA CATEGORÍA NO EXISTE
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "data": None,
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA EL GUARDADO DEL PRODUCTO
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible registrar el producto",
                "data": None,
                "success": False
            }
        )


# 3. BUSCAR PRODUCTOS POR NOMBRE O CÓDIGO
@router.get(
    "/buscar",
    status_code=status.HTTP_200_OK,
    summary="Buscar productos por nombre o código",
    description=(
        "Permite localizar productos registrados filtrando por nombre y/o código. "
        "Requiere ingresar al menos un criterio de búsqueda válido. "
        "Ejemplos: GET /api/v1/productos/buscar?nombre=Arroz o "
        "GET /api/v1/productos/buscar?codigo=PROD-001."
    ),
    responses={
        200: {
            "description": "Búsqueda de productos exitosa o sin coincidencias",
            "content": {
                "application/json": {
                    "examples": {
                        "con_coincidencias": {
                            "summary": "Productos encontrados",
                            "value": {
                                "message": "Búsqueda de productos exitosa",
                                "data": [
                                    {
                                        "id": 1,
                                        "nombre": "Arroz",
                                        "codigo": "PROD-001",
                                        "precio": 3500.0,
                                        "categoria_id": 1,
                                        "categoria": "Granos"
                                    }
                                ],
                                "success": True
                            }
                        },
                        "sin_coincidencias": {
                            "summary": "Sin coincidencias",
                            "value": {
                                "message": "No se encontraron productos con el criterio de búsqueda ingresado",
                                "data": [],
                                "success": True
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Criterio de búsqueda vacío o inválido",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Debe ingresar al menos un criterio de búsqueda (nombre o código)",
                        "data": [],
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno durante la búsqueda",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible realizar la búsqueda de productos",
                        "data": [],
                        "success": False
                    }
                }
            }
        }
    }
)
def BuscarProductosAPI(
    nombre: str | None = Query(
        default=None,
        description="NOMBRE DEL PRODUCTO A BUSCAR (SOLO LETRAS Y ESPACIOS)"
    ),
    codigo: str | None = Query(
        default=None,
        description="CÓDIGO DEL PRODUCTO A BUSCAR"
    ),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    # LIMPIAR ESPACIOS DE LOS CRITERIOS INGRESADOS
    nombre_limpio = nombre.strip() if isinstance(nombre, str) else None
    codigo_limpio = codigo.strip() if isinstance(codigo, str) else None

    # VALIDAR QUE SE HAYA INGRESADO AL MENOS UN CRITERIO DE BÚSQUEDA
    if not nombre_limpio and not codigo_limpio:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Debe ingresar al menos un criterio de búsqueda (nombre o código)",
                "data": [],
                "success": False
            }
        )

    # VALIDAR FORMATO DEL CRITERIO NOMBRE SI FUE PROPORCIONADO
    if nombre_limpio:
        if nombre_limpio.lower() in PALABRAS_PROHIBIDAS:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"El criterio nombre no puede contener el valor '{nombre_limpio}'",
                    "data": [],
                    "success": False
                }
            )
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+", nombre_limpio):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "El nombre de búsqueda solo debe contener letras y espacios",
                    "data": [],
                    "success": False
                }
            )

    # VALIDAR FORMATO DEL CRITERIO CÓDIGO SI FUE PROPORCIONADO
    if codigo_limpio:
        if codigo_limpio.lower() in PALABRAS_PROHIBIDAS:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"El criterio código no puede contener el valor '{codigo_limpio}'",
                    "data": [],
                    "success": False
                }
            )
        if not re.fullmatch(r"[a-zA-Z0-9\-_]+", codigo_limpio) or not any(c.isalnum() for c in codigo_limpio):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "El código de búsqueda solo debe contener letras, números, guiones o guiones bajos",
                    "data": [],
                    "success": False
                }
            )

    try:
        # EJECUTAR LA BÚSQUEDA EN EL SERVICIO DE PRODUCTOS
        productos = productoServicio.BuscarProductosServicio(
            nombre_limpio,
            codigo_limpio
        )

        if not productos:
            return {
                "message": "No se encontraron productos con el criterio de búsqueda ingresado",
                "data": [],
                "success": True
            }

        return {
            "message": "Búsqueda de productos exitosa",
            "data": productos,
            "success": True
        }

    except Exception:
        # RETORNAR ERROR CONTROLADO SI FALLA LA BÚSQUEDA
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible realizar la búsqueda de productos",
                "data": [],
                "success": False
            }
        )


# 4. CONSULTAR UN PRODUCTO POR ID
@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Consultar un producto por ID",
    description=(
        "Obtiene la información detallada de un producto específico (id, nombre, "
        "código, precio y categoría asociada) a partir de su identificador."
    ),
    responses={
        200: {
            "description": "Consulta de producto exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Consulta de producto exitosa",
                        "data": {
                            "id": 1,
                            "nombre": "Arroz",
                            "codigo": "PROD-001",
                            "precio": 3500.0,
                            "categoria_id": 1,
                            "categoria": "Granos"
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Producto no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No se encontró el producto solicitado",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al consultar el producto",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible consultar el producto",
                        "success": False
                    }
                }
            }
        }
    }
)
def ObtenerProductoPorIdAPI(
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PRODUCTO"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # BUSCAR EL PRODUCTO POR SU IDENTIFICADOR
        producto = productoServicio.ObtenerProductoPorIdServicio(id)

        if producto is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "No se encontró el producto solicitado",
                    "data": None,
                    "success": False
                }
            )

        return {
            "message": "Consulta de producto exitosa",
            "data": producto,
            "success": True
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar el producto",
                "data": None,
                "success": False
            }
        )


# 5. ACTUALIZAR UN PRODUCTO EXISTENTE
@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar un producto existente",
    description=(
        "Actualiza la información de un producto registrado (nombre, código, precio y "
        "categoría asociada) validando que el producto exista, que el código no esté "
        "asignado a otro producto, que la categoría exista y que el precio sea válido."
    ),
    responses={
        200: {
            "description": "Producto actualizado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Producto actualizado correctamente",
                        "data": {
                            "id": 1,
                            "nombre": "Arroz",
                            "codigo": "PROD-001",
                            "precio": 3800.0,
                            "categoria_id": 1,
                            "categoria": "Granos"
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Producto o categoría no encontrada",
            "content": {
                "application/json": {
                    "examples": {
                        "producto_inexistente": {
                            "summary": "Producto no existe",
                            "value": {
                                "message": "El producto seleccionado no existe",
                                "success": False
                            }
                        },
                        "categoria_inexistente": {
                            "summary": "Categoría no existe",
                            "value": {
                                "message": "La categoría seleccionada no existe",
                                "success": False
                            }
                        }
                    }
                }
            }
        },
        409: {
            "description": "Código asignado a otro producto",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El código del producto ya se encuentra registrado en otro producto",
                        "success": False
                    }
                }
            }
        },
        422: {
            "description": "Datos del producto incompletos o inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Faltan campos obligatorios: código.",
                        "success": False,
                        "errors": [
                            {
                                "campo": "código",
                                "mensaje": "Debe completar el campo código."
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno al guardar los cambios",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible actualizar el producto",
                        "success": False
                    }
                }
            }
        }
    }
)
def ActualizarProductoAPI(
    datos: ProductoActualizar,
    id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PRODUCTO"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        # INVOCAR EL SERVICIO PARA ACTUALIZAR EL PRODUCTO
        producto = productoServicio.ActualizarProductoServicio(
            id,
            datos.model_dump()
        )

        # RETORNAR RESPUESTA DE ACTUALIZACIÓN EXITOSA
        return {
            "message": "Producto actualizado correctamente",
            "data": producto,
            "success": True
        }

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI EL PRODUCTO O LA CATEGORÍA NO EXISTEN
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "data": None,
                "success": False
            }
        )

    except ValueError as error:
        # RETORNAR CONFLICTO SI EL CÓDIGO YA PERTENECE A OTRO PRODUCTO
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "data": None,
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA EL GUARDADO DE LOS CAMBIOS
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible actualizar el producto",
                "data": None,
                "success": False
            }
        )
