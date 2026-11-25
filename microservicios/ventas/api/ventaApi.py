from fastapi import APIRouter, Body, Path, status, Depends
from fastapi.responses import JSONResponse

from microservicios.usuarios.api.usuarioApi import ObtenerSuperadministrador
from microservicios.ventas.api.dtos import (
    ConfirmarVentaSolicitud,
    DetalleVentaActualizar,
    DetalleVentaAgregar,
    ValidarInventarioVentaSolicitud,
    VentaRegistro
)
from microservicios.ventas.servicio import ventaServicio


# CONFIGURAR EL ROUTER DEL MICROSERVICIO DE VENTAS
router = APIRouter(
    prefix="/api/v1/ventas",
    tags=["Gestión de ventas"]
)


# REGISTRAR UNA NUEVA VENTA ASOCIADA A UN CLIENTE EN ESTADO PENDIENTE
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una venta asociada a un cliente",
    description=(
        "Inicia el registro de una nueva venta en estado pendiente asociándola a un "
        "cliente previamente registrado en el sistema. Permite continuar posteriormente "
        "con el registro de productos y cantidades."
    ),
    responses={
        201: {
            "description": "Venta iniciada correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Venta iniciada correctamente",
                        "data": {
                            "venta_id": 1,
                            "cliente_id": 1,
                            "estado": "pendiente",
                            "productos": []
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "El cliente seleccionado no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El cliente seleccionado no existe",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al registrar la venta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible registrar la venta",
                        "success": False
                    }
                }
            }
        }
    }
)
def RegistrarVentaAPI(
    datos: VentaRegistro,
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        venta = ventaServicio.RegistrarVentaServicio(datos.model_dump())
        return {
            "message": "Venta iniciada correctamente",
            "data": venta,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible registrar la venta",
                "success": False
            }
        )


# CONSULTAR TODAS LAS VENTAS REGISTRADAS
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Consultar ventas registradas",
    description="Obtiene el listado de ventas registradas con su estado y productos."
)
def ConsultarVentasAPI(
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        ventas = ventaServicio.ConsultarVentasServicio()

        if not ventas:
            return {
                "message": "No existen ventas registradas",
                "data": [],
                "success": True
            }

        return {
            "message": "Consulta de ventas exitosa",
            "data": ventas,
            "success": True
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar las ventas",
                "data": [],
                "success": False
            }
        )


# CONFIRMAR UNA VENTA Y DESCONTAR EXISTENCIAS DEL INVENTARIO
@router.post(
    "/{venta_id}/confirmar",
    status_code=status.HTTP_200_OK,
    summary="Confirmar venta y descontar existencias del inventario",
    description=(
        "Confirma una venta registrada en estado pendiente y descuenta automáticamente "
        "las cantidades vendidas del inventario. Valida que la venta exista, que no haya "
        "sido confirmada previamente, que todos los productos tengan existencias suficientes "
        "y garantiza consistencia ante errores."
    ),
    responses={
        200: {
            "description": "Venta confirmada e inventario actualizado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Venta confirmada e inventario actualizado correctamente",
                        "data": {
                            "venta_id": 1,
                            "estado": "confirmada",
                            "productos": [
                                {
                                    "producto_id": 1,
                                    "cantidad_vendida": 5,
                                    "existencias_anteriores": 100,
                                    "existencias_actuales": 95
                                },
                                {
                                    "producto_id": 2,
                                    "cantidad_vendida": 3,
                                    "existencias_anteriores": 20,
                                    "existencias_actuales": 17
                                }
                            ]
                        },
                        "success": True
                    }
                }
            }
        },
        400: {
            "description": "El identificador de la venta en el cuerpo no coincide con la ruta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El identificador de la venta en la solicitud no coincide con el de la ruta",
                        "success": False
                    }
                }
            }
        },
        404: {
            "description": "La venta seleccionada no existe",
            "content": {
                "application/json": {
                    "example": {
                        "message": "La venta seleccionada no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "Existencias insuficientes o venta ya confirmada",
            "content": {
                "application/json": {
                    "examples": {
                        "existencias_insuficientes": {
                            "summary": "Inventario insuficiente",
                            "value": {
                                "message": "No hay suficiente inventario para completar la operación: producto ID 1 (solicitado: 150, disponible: 100)",
                                "success": False
                            }
                        },
                        "venta_ya_confirmada": {
                            "summary": "Venta ya confirmada previamente",
                            "value": {
                                "message": "La venta ya fue confirmada y sus existencias ya fueron descontadas",
                                "success": False
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al actualizar el inventario o confirmar la venta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible confirmar la venta y actualizar el inventario",
                        "success": False
                    }
                }
            }
        }
    }
)
def ConfirmarVentaAPI(
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    datos: ConfirmarVentaSolicitud | None = Body(default=None),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    # VALIDAR COHERENCIA SI SE ENVÍA venta_id EN EL CUERPO DE LA SOLICITUD
    if datos is not None and datos.venta_id != venta_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "El identificador de la venta en la solicitud no coincide con el de la ruta",
                "success": False
            }
        )

    try:
        # INVOCAR EL SERVICIO PARA CONFIRMAR LA VENTA Y DESCONTAR EXISTENCIAS
        resultado = ventaServicio.ConfirmarVentaServicio(venta_id)

        return {
            "message": "Venta confirmada e inventario actualizado correctamente",
            "data": resultado,
            "success": True
        }

    except LookupError as error:
        # RETORNAR NO ENCONTRADO SI LA VENTA NO EXISTE
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        # RETORNAR CONFLICTO SI FALTAN EXISTENCIAS O LA VENTA YA FUE CONFIRMADA
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        # RETORNAR ERROR INTERNO SI FALLA LA ACTUALIZACIÓN DEL INVENTARIO
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible confirmar la venta y actualizar el inventario",
                "success": False
            }
        )


# AGREGAR UN PRODUCTO Y CANTIDAD AL DETALLE DE UNA VENTA PENDIENTE
@router.post(
    "/{venta_id}/detalles",
    status_code=status.HTTP_201_CREATED,
    summary="Agregar producto y cantidad al detalle de una venta",
    description=(
        "Agrega un producto registrado y su cantidad (entero positivo) al detalle "
        "de una venta en estado pendiente. Si el producto ya existe en el detalle, "
        "acumula la cantidad."
    ),
    responses={
        201: {
            "description": "Producto agregado correctamente al detalle de la venta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Producto agregado correctamente al detalle de la venta",
                        "data": {
                            "venta_id": 1,
                            "producto_id": 15,
                            "cantidad": 2
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Venta o producto no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El producto seleccionado no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "La venta ya fue confirmada y no permite modificaciones",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No se puede modificar el detalle de una venta que ya fue confirmada",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al agregar el producto al detalle",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible agregar el producto al detalle de la venta",
                        "success": False
                    }
                }
            }
        }
    }
)
def AgregarDetalleVentaAPI(
    datos: DetalleVentaAgregar,
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        detalle = ventaServicio.AgregarDetalleVentaServicio(
            venta_id,
            datos.model_dump()
        )
        return {
            "message": "Producto agregado correctamente al detalle de la venta",
            "data": detalle,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible agregar el producto al detalle de la venta",
                "success": False
            }
        )


# CONSULTAR EL DETALLE DE PRODUCTOS Y CANTIDADES DE UNA VENTA
@router.get(
    "/{venta_id}/detalles",
    status_code=status.HTTP_200_OK,
    summary="Consultar detalle de una venta",
    description="Obtiene los productos y cantidades agregadas al detalle de una venta."
)
def ConsultarDetalleVentaAPI(
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        detalles = ventaServicio.ConsultarDetalleVentaServicio(venta_id)

        if not detalles:
            return {
                "message": "El detalle de la venta está vacío",
                "data": [],
                "success": True
            }

        return {
            "message": "Consulta del detalle de la venta exitosa",
            "data": detalles,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "data": [],
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible consultar el detalle de la venta",
                "data": [],
                "success": False
            }
        )


# MODIFICAR LA CANTIDAD DE UN PRODUCTO EN EL DETALLE DE UNA VENTA PENDIENTE
@router.put(
    "/{venta_id}/detalles/{producto_id}",
    status_code=status.HTTP_200_OK,
    summary="Modificar la cantidad de un producto en el detalle",
    description="Actualiza la cantidad de un producto previamente agregado al detalle de una venta pendiente."
)
def ActualizarDetalleVentaAPI(
    datos: DetalleVentaActualizar,
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    producto_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PRODUCTO"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        detalle = ventaServicio.ActualizarDetalleVentaServicio(
            venta_id,
            producto_id,
            datos.cantidad
        )
        return {
            "message": "Cantidad del producto actualizada correctamente",
            "data": detalle,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible actualizar la cantidad del producto",
                "success": False
            }
        )


# RETIRAR UN PRODUCTO DEL DETALLE DE UNA VENTA PENDIENTE
@router.delete(
    "/{venta_id}/detalles/{producto_id}",
    status_code=status.HTTP_200_OK,
    summary="Retirar un producto del detalle de una venta",
    description="Elimina un producto del detalle de una venta pendiente antes de confirmarla."
)
def EliminarDetalleVentaAPI(
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    producto_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DEL PRODUCTO"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        resultado = ventaServicio.EliminarDetalleVentaServicio(
            venta_id,
            producto_id
        )
        return {
            "message": "Producto retirado del detalle de la venta correctamente",
            "data": resultado,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible retirar el producto del detalle de la venta",
                "success": False
            }
        )


# CALCULAR SUBTOTALES Y TOTAL DE UNA VENTA
@router.get(
    "/{venta_id}/totales",
    status_code=status.HTTP_200_OK,
    summary="Calcular subtotales y total de una venta",
    description=(
        "Calcula automáticamente el subtotal de cada producto incluido en el detalle "
        "(subtotal = precio_unitario * cantidad) y el importe total de la venta "
        "(total_venta = suma de todos los subtotales). Rechaza el cálculo si la venta "
        "no tiene productos o si algún producto presenta un precio inválido."
    ),
    responses={
        200: {
            "description": "Cálculo de la venta realizado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Cálculo de la venta realizado correctamente",
                        "data": {
                            "venta_id": 1,
                            "productos": [
                                {
                                    "producto_id": 15,
                                    "nombre": "Producto A",
                                    "precio_unitario": 10000.0,
                                    "cantidad": 2,
                                    "subtotal": 20000.0
                                },
                                {
                                    "producto_id": 18,
                                    "nombre": "Producto B",
                                    "precio_unitario": 5000.0,
                                    "cantidad": 3,
                                    "subtotal": 15000.0
                                }
                            ],
                            "total_venta": 35000.0
                        },
                        "success": True
                    }
                }
            }
        },
        404: {
            "description": "Venta o producto no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "La venta seleccionada no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "Detalle vacío, cantidad inválida o precio inválido",
            "content": {
                "application/json": {
                    "examples": {
                        "detalle_vacio": {
                            "summary": "Venta sin productos",
                            "value": {
                                "message": "Debe agregar al menos un producto al detalle de la venta",
                                "success": False
                            }
                        },
                        "precio_invalido": {
                            "summary": "Producto con precio inválido",
                            "value": {
                                "message": "El producto 'Arroz' presenta un problema con su precio",
                                "success": False
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Error interno al calcular los totales de la venta",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible calcular los totales de la venta",
                        "success": False
                    }
                }
            }
        }
    }
)
def CalcularTotalesVentaAPI(
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        totales = ventaServicio.CalcularTotalesVentaServicio(venta_id)
        return {
            "message": "Cálculo de la venta realizado correctamente",
            "data": totales,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible calcular los totales de la venta",
                "success": False
            }
        )


# VALIDAR LA DISPONIBILIDAD DE INVENTARIO ANTES DE CONFIRMAR UNA VENTA
@router.post(
    "/{venta_id}/validar-inventario",
    status_code=status.HTTP_200_OK,
    summary="Validar disponibilidad de inventario de una venta",
    description=(
        "Consulta las existencias actuales de cada producto incluido en la venta "
        "(o en la lista enviada) y compara las cantidades solicitadas contra el inventario "
        "disponible antes de permitir la confirmación."
    ),
    responses={
        200: {
            "description": "Resultado de la validación de inventario de la venta",
            "content": {
                "application/json": {
                    "examples": {
                        "existencias_suficientes": {
                            "summary": "Todos los productos disponibles",
                            "value": {
                                "message": "Validación de inventario realizada correctamente",
                                "data": {
                                    "venta_id": 1,
                                    "disponibilidad_suficiente": True,
                                    "productos": [
                                        {
                                            "producto_id": 15,
                                            "cantidad_solicitada": 2,
                                            "existencias_disponibles": 10,
                                            "disponible": True
                                        },
                                        {
                                            "producto_id": 18,
                                            "cantidad_solicitada": 3,
                                            "existencias_disponibles": 8,
                                            "disponible": True
                                        }
                                    ]
                                },
                                "success": True
                            }
                        },
                        "existencias_insuficientes": {
                            "summary": "Uno o más productos sin stock suficiente",
                            "value": {
                                "message": "No hay existencias suficientes para todos los productos",
                                "data": {
                                    "venta_id": 1,
                                    "disponibilidad_suficiente": False,
                                    "productos": [
                                        {
                                            "producto_id": 15,
                                            "cantidad_solicitada": 5,
                                            "existencias_disponibles": 2,
                                            "disponible": False
                                        }
                                    ]
                                },
                                "success": False
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Venta o producto no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "message": "El producto con ID 999 no existe",
                        "success": False
                    }
                }
            }
        },
        409: {
            "description": "La venta no tiene productos en su detalle",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Debe agregar al menos un producto al detalle de la venta",
                        "success": False
                    }
                }
            }
        },
        500: {
            "description": "Error interno al validar el inventario",
            "content": {
                "application/json": {
                    "example": {
                        "message": "No fue posible validar la disponibilidad del inventario",
                        "success": False
                    }
                }
            }
        }
    }
)
def ValidarInventarioVentaAPI(
    venta_id: int = Path(..., gt=0, description="IDENTIFICADOR NUMÉRICO DE LA VENTA"),
    datos: ValidarInventarioVentaSolicitud | None = Body(default=None),
    usuario_autenticado: dict = Depends(ObtenerSuperadministrador)
):
    try:
        productos_solicitud = (
            datos.model_dump()["productos"]
            if datos is not None and datos.productos is not None
            else None
        )

        resultado = ventaServicio.ValidarInventarioVentaServicio(
            venta_id,
            productos_solicitud
        )

        if not resultado["disponibilidad_suficiente"]:
            return {
                "message": "No hay existencias suficientes para todos los productos",
                "data": resultado,
                "success": False
            }

        return {
            "message": "Validación de inventario realizada correctamente",
            "data": resultado,
            "success": True
        }

    except LookupError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": str(error),
                "success": False
            }
        )

    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": str(error),
                "success": False
            }
        )

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "No fue posible validar la disponibilidad del inventario",
                "success": False
            }
        )
