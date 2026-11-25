import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.clientes.repositorio import clienteRepositorio
from microservicios.inventario.api.dtos import ExistenciasInicialesRegistro
from microservicios.inventario.api.inventarioApi import RegistrarExistenciasInicialesAPI
from microservicios.inventario.repositorio import inventarioRepositorio
from microservicios.inventario.servicio import inventarioServicio
from microservicios.productos.repositorio import productoRepositorio
from microservicios.ventas.api.dtos import (
    ConfirmarVentaSolicitud,
    DetalleVentaActualizar,
    DetalleVentaAgregar,
    ValidarInventarioVentaSolicitud,
    VentaRegistro
)
from microservicios.ventas.api.ventaApi import (
    ActualizarDetalleVentaAPI,
    AgregarDetalleVentaAPI,
    CalcularTotalesVentaAPI,
    ConfirmarVentaAPI,
    ConsultarDetalleVentaAPI,
    ConsultarVentasAPI,
    EliminarDetalleVentaAPI,
    ObtenerVentaPorIdAPI,
    RegistrarVentaAPI,
    ValidarInventarioVentaAPI
)
from microservicios.ventas.repositorio import ventaRepositorio


# PRUEBAS UNITARIAS PARA CONFIRMAR VENTAS Y DESCONTAR EXISTENCIAS DEL INVENTARIO
class TestConfirmacionVentasInventario(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        # REGISTRAR CLIENTE, CATEGORÍA, PRODUCTOS Y EXISTENCIAS INICIALES
        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "1234567890",
            "nombre": "Juan Perez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Arroz",
            "codigo": "PROD-001",
            "precio": 3500.0,
            "categoria_id": 1
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Aceite",
            "codigo": "PROD-002",
            "precio": 6500.0,
            "categoria_id": 1
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=1, cantidad_inicial=100),
            self.usuario_autenticado
        )
        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=2, cantidad_inicial=20),
            self.usuario_autenticado
        )

    # CASO 1: DESCUENTO EXITOSO DE EXISTENCIAS AL CONFIRMAR UNA VENTA
    def test_descuento_exitoso_al_confirmar_venta(self):
        RegistrarVentaAPI(
            VentaRegistro(
                cliente_id=1,
                productos=[
                    {"producto_id": 1, "cantidad": 5},
                    {"producto_id": 2, "cantidad": 3}
                ]
            ),
            self.usuario_autenticado
        )

        respuesta = ConfirmarVentaAPI(
            venta_id=1,
            datos=ConfirmarVentaSolicitud(venta_id=1),
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "Venta confirmada e inventario actualizado correctamente"
        )
        self.assertEqual(respuesta["data"]["venta_id"], 1)
        self.assertEqual(respuesta["data"]["estado"], "confirmada")
        self.assertEqual(respuesta["data"]["productos"][0]["existencias_anteriores"], 100)
        self.assertEqual(respuesta["data"]["productos"][0]["existencias_actuales"], 95)
        self.assertEqual(respuesta["data"]["productos"][1]["existencias_anteriores"], 20)
        self.assertEqual(respuesta["data"]["productos"][1]["existencias_actuales"], 17)

        # VERIFICAR QUE EL INVENTARIO QUEDÓ ACTUALIZADO
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(1)["cantidad_inicial"],
            95
        )
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(2)["cantidad_inicial"],
            17
        )

    # CASO 2: EXISTENCIAS INSUFICIENTES PARA CONFIRMAR LA VENTA
    def test_existencias_insuficientes_impide_confirmar(self):
        RegistrarVentaAPI(
            VentaRegistro(
                cliente_id=1,
                productos=[
                    {"producto_id": 1, "cantidad": 5},
                    {"producto_id": 2, "cantidad": 50}
                ]
            ),
            self.usuario_autenticado
        )

        respuesta = ConfirmarVentaAPI(
            venta_id=1,
            datos=None,
            usuario_autenticado=self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertIn("No hay suficiente inventario", cuerpo["message"])

        # VERIFICAR QUE EL INVENTARIO Y EL ESTADO DE LA VENTA PERMANECEN INTACTOS
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(1)["cantidad_inicial"],
            100
        )
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(2)["cantidad_inicial"],
            20
        )
        self.assertEqual(ventaRepositorio.ObtenerVentaPorIdRepositorio(1)["estado"], "pendiente")

    # CASO 3: INTENTO DE DESCONTAR EXISTENCIAS DE UNA VENTA NO CONFIRMADA
    def test_impedir_descuento_de_venta_no_confirmada(self):
        venta = RegistrarVentaAPI(
            VentaRegistro(cliente_id=1, productos=[{"producto_id": 1, "cantidad": 5}]),
            self.usuario_autenticado
        )["data"]

        with self.assertRaises(ValueError):
            inventarioServicio.DescontarExistenciasVentaServicio(
                venta["productos"],
                venta["estado"]
            )

        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(1)["cantidad_inicial"],
            100
        )
        self.assertEqual(ventaRepositorio.ObtenerVentaPorIdRepositorio(1)["estado"], "pendiente")

    # CASO 4: EVITAR EL DESCUENTO DUPLICADO EN UNA VENTA YA CONFIRMADA
    def test_evitar_descuento_duplicado(self):
        RegistrarVentaAPI(
            VentaRegistro(cliente_id=1, productos=[{"producto_id": 1, "cantidad": 5}]),
            self.usuario_autenticado
        )

        ConfirmarVentaAPI(1, None, self.usuario_autenticado)

        # SEGUNDO INTENTO DE CONFIRMACIÓN
        respuesta = ConfirmarVentaAPI(1, None, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertIn("ya fue confirmada", cuerpo["message"])
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(1)["cantidad_inicial"],
            95
        )

    # CASO 5: ERROR DURANTE LA ACTUALIZACIÓN DEL INVENTARIO CON REVERSIÓN CONSISTENTE
    @patch(
        "microservicios.inventario.repositorio.inventarioRepositorio.ActualizarCantidadInventarioRepositorio",
        side_effect=[{"producto_id": 1, "cantidad_inicial": 95}, None, {"producto_id": 1, "cantidad_inicial": 100}]
    )
    def test_error_actualizacion_inventario_mantiene_consistencia(self, mock_actualizar):
        RegistrarVentaAPI(
            VentaRegistro(
                cliente_id=1,
                productos=[
                    {"producto_id": 1, "cantidad": 5},
                    {"producto_id": 2, "cantidad": 3}
                ]
            ),
            self.usuario_autenticado
        )

        respuesta = ConfirmarVentaAPI(1, None, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "No fue posible confirmar la venta y actualizar el inventario"
        )
        self.assertEqual(ventaRepositorio.ObtenerVentaPorIdRepositorio(1)["estado"], "pendiente")

    # VALIDAR VENTA INEXISTENTE Y VALIDACIONES ESTRICTAS DE DTOS
    def test_venta_inexistente_y_validaciones_dtos(self):
        respuesta = ConfirmarVentaAPI(999, None, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "La venta seleccionada no existe")

        for valor_invalido in [0, -1, 1.5, "string", True]:
            with self.assertRaises(ValidationError):
                ConfirmarVentaSolicitud(venta_id=valor_invalido)

    # VERIFICAR QUE LOS ENDPOINTS DE VENTAS ESTÉN EN OPENAPI / SWAGGER
    def test_documentacion_openapi_ventas(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/ventas/", esquema["paths"])
        self.assertIn("/api/v1/ventas/{venta_id}/confirmar", esquema["paths"])
        self.assertIn("post", esquema["paths"]["/api/v1/ventas/{venta_id}/confirmar"])


# PRUEBAS UNITARIAS PARA REGISTRAR UNA VENTA SELECCIONANDO UN CLIENTE
class TestRegistroVentaCliente(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "1234567890",
            "nombre": "Juan Perez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: REGISTRO DE UNA VENTA CON UN CLIENTE EXISTENTE
    def test_registro_venta_cliente_existente(self):
        datos = VentaRegistro(cliente_id=1)

        respuesta = RegistrarVentaAPI(datos, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Venta iniciada correctamente")
        self.assertEqual(respuesta["data"]["venta_id"], 1)
        self.assertEqual(respuesta["data"]["cliente_id"], 1)
        self.assertEqual(respuesta["data"]["estado"], "pendiente")

    # CASO 2: INTENTO DE REGISTRAR UNA VENTA CON UN CLIENTE INEXISTENTE
    def test_registro_venta_cliente_inexistente(self):
        datos = VentaRegistro(cliente_id=999)

        respuesta = RegistrarVentaAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El cliente seleccionado no existe")
        self.assertEqual(len(ventaRepositorio.ventas), 0)

    # CASO 3: REGISTRO DE UNA VENTA SIN SELECCIONAR CLIENTE O CON CLIENTE INVÁLIDO
    def test_registro_venta_sin_cliente_o_invalido(self):
        with self.assertRaises(ValidationError) as contexto:
            VentaRegistro()

        campos = [error["loc"][0] for error in contexto.exception.errors()]
        self.assertIn("cliente_id", campos)

        for valor_invalido in [0, -1, 1.5, "string", True, None]:
            with self.assertRaises(ValidationError):
                VentaRegistro(cliente_id=valor_invalido)

        self.assertEqual(len(ventaRepositorio.ventas), 0)

    # CASO 4: VERIFICACIÓN DE LA ASOCIACIÓN ENTRE VENTA Y CLIENTE
    def test_verificacion_asociacion_venta_cliente(self):
        RegistrarVentaAPI(VentaRegistro(cliente_id=1), self.usuario_autenticado)

        consulta = ConsultarVentasAPI(self.usuario_autenticado)
        self.assertTrue(consulta["success"])
        self.assertEqual(len(consulta["data"]), 1)
        self.assertEqual(consulta["data"][0]["id"], 1)
        self.assertEqual(consulta["data"][0]["cliente_id"], 1)
        self.assertEqual(consulta["data"][0]["estado"], "pendiente")

    # CASO 5: ERROR DURANTE EL REGISTRO DE LA VENTA
    @patch(
        "microservicios.ventas.repositorio.ventaRepositorio.RegistrarVentaRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_registro_venta(self, mock_guardar):
        datos = VentaRegistro(cliente_id=1)

        respuesta = RegistrarVentaAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible registrar la venta")
        self.assertEqual(len(ventaRepositorio.ventas), 0)


# PRUEBAS UNITARIAS PARA AGREGAR, MODIFICAR Y RETIRAR PRODUCTOS DEL DETALLE DE UNA VENTA
class TestDetalleVenta(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "1234567890",
            "nombre": "Juan Perez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Arroz",
            "codigo": "PROD-001",
            "precio": 3500.0,
            "categoria_id": 1
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Aceite",
            "codigo": "PROD-002",
            "precio": 6500.0,
            "categoria_id": 1
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarVentaAPI(VentaRegistro(cliente_id=1), self.usuario_autenticado)

    # CASO 1: AGREGAR UN PRODUCTO CORRECTAMENTE AL DETALLE DE LA VENTA
    def test_agregar_producto_detalle_venta(self):
        respuesta = AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            venta_id=1,
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "Producto agregado correctamente al detalle de la venta"
        )
        self.assertEqual(respuesta["data"]["venta_id"], 1)
        self.assertEqual(respuesta["data"]["producto_id"], 1)
        self.assertEqual(respuesta["data"]["cantidad"], 2)

        detalle = ConsultarDetalleVentaAPI(1, self.usuario_autenticado)
        self.assertEqual(len(detalle["data"]), 1)
        self.assertEqual(detalle["data"][0]["nombre_producto"], "Arroz")

    # CASO 2: AGREGAR VARIOS PRODUCTOS A UNA VENTA
    def test_agregar_varios_productos_venta(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=4),
            1,
            self.usuario_autenticado
        )

        detalle = ConsultarDetalleVentaAPI(1, self.usuario_autenticado)
        self.assertTrue(detalle["success"])
        self.assertEqual(len(detalle["data"]), 2)
        self.assertEqual(detalle["data"][0]["cantidad"], 2)
        self.assertEqual(detalle["data"][1]["cantidad"], 4)

    # CASO 3: MODIFICAR LA CANTIDAD DE UN PRODUCTO EN EL DETALLE
    def test_modificar_cantidad_producto_detalle(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=4),
            1,
            self.usuario_autenticado
        )

        respuesta = ActualizarDetalleVentaAPI(
            DetalleVentaActualizar(cantidad=7),
            venta_id=1,
            producto_id=1,
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["data"]["cantidad"], 7)

        detalle = ConsultarDetalleVentaAPI(1, self.usuario_autenticado)
        self.assertEqual(detalle["data"][0]["cantidad"], 7)
        self.assertEqual(detalle["data"][1]["cantidad"], 4)

    # CASO 4: RETIRAR UN PRODUCTO DEL DETALLE ANTES DE CONFIRMAR
    def test_retirar_producto_detalle_venta(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=4),
            1,
            self.usuario_autenticado
        )

        respuesta = EliminarDetalleVentaAPI(
            venta_id=1,
            producto_id=1,
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        detalle = ConsultarDetalleVentaAPI(1, self.usuario_autenticado)
        self.assertEqual(len(detalle["data"]), 1)
        self.assertEqual(detalle["data"][0]["producto_id"], 2)

    # CASO 5: INGRESAR UNA CANTIDAD INVÁLIDA O PRODUCTO INEXISTENTE
    def test_cantidad_invalida_o_producto_inexistente(self):
        for cantidad_invalida in [0, -2, 1.5, "string", True, None]:
            with self.assertRaises(ValidationError):
                DetalleVentaAgregar(producto_id=1, cantidad=cantidad_invalida)
            with self.assertRaises(ValidationError):
                DetalleVentaActualizar(cantidad=cantidad_invalida)

        respuesta = AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=999, cantidad=2),
            venta_id=1,
            usuario_autenticado=self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El producto seleccionado no existe")

    # CASO 6: INTENTAR CONTINUAR/CONFIRMAR UNA VENTA SIN PRODUCTOS EN SU DETALLE
    def test_impedir_continuar_venta_detalle_vacio(self):
        respuesta = ConfirmarVentaAPI(1, None, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "Debe agregar al menos un producto al detalle de la venta"
        )

    # VERIFICAR QUE LOS ENDPOINTS DE DETALLE ESTÉN EN OPENAPI / SWAGGER
    def test_documentacion_openapi_detalle_venta(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/ventas/{venta_id}/detalles", esquema["paths"])
        self.assertIn("post", esquema["paths"]["/api/v1/ventas/{venta_id}/detalles"])
        self.assertIn("get", esquema["paths"]["/api/v1/ventas/{venta_id}/detalles"])
        self.assertIn("/api/v1/ventas/{venta_id}/detalles/{producto_id}", esquema["paths"])
        self.assertIn(
            "put",
            esquema["paths"]["/api/v1/ventas/{venta_id}/detalles/{producto_id}"]
        )
        self.assertIn(
            "delete",
            esquema["paths"]["/api/v1/ventas/{venta_id}/detalles/{producto_id}"]
        )


# PRUEBAS UNITARIAS PARA CALCULAR SUBTOTALES Y TOTAL DE UNA VENTA
class TestTotalesVenta(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "1234567890",
            "nombre": "Juan Perez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Producto A",
            "codigo": "PROD-015",
            "precio": 10000.0,
            "categoria_id": 1
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Producto B",
            "codigo": "PROD-018",
            "precio": 5000.0,
            "categoria_id": 1
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarVentaAPI(VentaRegistro(cliente_id=1), self.usuario_autenticado)

    # CASO 1: CALCULAR EL SUBTOTAL DE UN PRODUCTO
    def test_calcular_subtotal_un_producto(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )

        respuesta = CalcularTotalesVentaAPI(1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Cálculo de la venta realizado correctamente")
        self.assertEqual(respuesta["data"]["productos"][0]["precio_unitario"], 10000.0)
        self.assertEqual(respuesta["data"]["productos"][0]["cantidad"], 2)
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 20000.0)
        self.assertEqual(respuesta["data"]["total_venta"], 20000.0)

    # CASO 2: CALCULAR EL TOTAL DE VARIOS PRODUCTOS
    def test_calcular_total_varios_productos(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=3),
            1,
            self.usuario_autenticado
        )

        respuesta = CalcularTotalesVentaAPI(1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 20000.0)
        self.assertEqual(respuesta["data"]["productos"][1]["subtotal"], 15000.0)
        self.assertEqual(respuesta["data"]["total_venta"], 35000.0)

    # CASO 3: RECALCULAR DESPUÉS DE MODIFICAR UNA CANTIDAD
    def test_recalcular_al_modificar_cantidad(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=3),
            1,
            self.usuario_autenticado
        )

        ActualizarDetalleVentaAPI(
            DetalleVentaActualizar(cantidad=4),
            venta_id=1,
            producto_id=1,
            usuario_autenticado=self.usuario_autenticado
        )

        respuesta = CalcularTotalesVentaAPI(1, self.usuario_autenticado)
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 40000.0)
        self.assertEqual(respuesta["data"]["total_venta"], 55000.0)

    # CASO 4: RECALCULAR DESPUÉS DE RETIRAR UN PRODUCTO
    def test_recalcular_al_retirar_producto(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=3),
            1,
            self.usuario_autenticado
        )

        EliminarDetalleVentaAPI(1, 1, self.usuario_autenticado)

        respuesta = CalcularTotalesVentaAPI(1, self.usuario_autenticado)
        self.assertEqual(len(respuesta["data"]["productos"]), 1)
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 15000.0)
        self.assertEqual(respuesta["data"]["total_venta"], 15000.0)

    # CASO 5: INTENTAR CALCULAR UNA VENTA SIN PRODUCTOS
    def test_impedir_calculo_venta_sin_productos(self):
        respuesta = CalcularTotalesVentaAPI(1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "Debe agregar al menos un producto al detalle de la venta"
        )

    # CASO 6: PRODUCTO CON PRECIO INVÁLIDO
    def test_producto_con_precio_invalido(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        productoRepositorio.ObtenerProductoPorIdRepositorio(1)["precio"] = -100

        respuesta = CalcularTotalesVentaAPI(1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertIn("presenta un problema con su precio", cuerpo["message"])

    # VERIFICAR QUE EL ENDPOINT DE TOTALES ESTÉ EN OPENAPI / SWAGGER
    def test_documentacion_openapi_totales_venta(self):
        esquema = app.openapi()
        ruta = "/api/v1/ventas/{venta_id}/totales"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta])


# PRUEBAS UNITARIAS PARA VALIDAR INVENTARIO ANTES DE CONFIRMAR UNA VENTA
class TestValidarInventarioVenta(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "1234567890",
            "nombre": "Juan Perez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Arroz",
            "codigo": "PROD-001",
            "precio": 3500.0,
            "categoria_id": 1
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Aceite",
            "codigo": "PROD-002",
            "precio": 6500.0,
            "categoria_id": 1
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Azúcar",
            "codigo": "PROD-003",
            "precio": 2500.0,
            "categoria_id": 1
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=1, cantidad_inicial=10),
            self.usuario_autenticado
        )
        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=2, cantidad_inicial=8),
            self.usuario_autenticado
        )
        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=3, cantidad_inicial=0),
            self.usuario_autenticado
        )

        RegistrarVentaAPI(VentaRegistro(cliente_id=1), self.usuario_autenticado)

    # CASO 1: TODOS LOS PRODUCTOS TIENEN EXISTENCIAS SUFICIENTES
    def test_validar_inventario_existencias_suficientes(self):
        datos = ValidarInventarioVentaSolicitud(
            productos=[
                {"producto_id": 1, "cantidad": 2},
                {"producto_id": 2, "cantidad": 3}
            ]
        )

        respuesta = ValidarInventarioVentaAPI(1, datos, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "Validación de inventario realizada correctamente"
        )
        self.assertTrue(respuesta["data"]["disponibilidad_suficiente"])
        self.assertEqual(respuesta["data"]["productos"][0]["existencias_disponibles"], 10)
        self.assertTrue(respuesta["data"]["productos"][0]["disponible"])

    # CASO 2: UN PRODUCTO TIENE EXISTENCIAS INSUFICIENTES
    def test_validar_inventario_existencias_insuficientes(self):
        datos = ValidarInventarioVentaSolicitud(
            productos=[
                {"producto_id": 1, "cantidad": 15}
            ]
        )

        respuesta = ValidarInventarioVentaAPI(1, datos, self.usuario_autenticado)

        self.assertFalse(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "No hay existencias suficientes para todos los productos"
        )
        self.assertFalse(respuesta["data"]["disponibilidad_suficiente"])
        self.assertEqual(respuesta["data"]["productos"][0]["cantidad_solicitada"], 15)
        self.assertEqual(respuesta["data"]["productos"][0]["existencias_disponibles"], 10)
        self.assertFalse(respuesta["data"]["productos"][0]["disponible"])

    # CASO 3: PRODUCTO SIN EXISTENCIAS (CERO UNIDADES DISPONIBLES)
    def test_validar_inventario_producto_sin_existencias(self):
        datos = ValidarInventarioVentaSolicitud(
            productos=[
                {"producto_id": 3, "cantidad": 1}
            ]
        )

        respuesta = ValidarInventarioVentaAPI(1, datos, self.usuario_autenticado)

        self.assertFalse(respuesta["success"])
        self.assertFalse(respuesta["data"]["disponibilidad_suficiente"])
        self.assertEqual(respuesta["data"]["productos"][0]["existencias_disponibles"], 0)
        self.assertFalse(respuesta["data"]["productos"][0]["disponible"])

    # CASO 4: MODIFICAR LA CANTIDAD DE UN PRODUCTO Y VOLVER A VALIDAR
    def test_validar_inventario_despues_de_modificar_cantidad(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=15),
            1,
            self.usuario_autenticado
        )

        primera = ValidarInventarioVentaAPI(1, None, self.usuario_autenticado)
        self.assertFalse(primera["data"]["disponibilidad_suficiente"])

        ActualizarDetalleVentaAPI(
            DetalleVentaActualizar(cantidad=5),
            1,
            1,
            self.usuario_autenticado
        )

        segunda = ValidarInventarioVentaAPI(1, None, self.usuario_autenticado)
        self.assertTrue(segunda["success"])
        self.assertTrue(segunda["data"]["disponibilidad_suficiente"])

    # CASO 5: LAS EXISTENCIAS CAMBIAN ANTES DE CONFIRMAR LA VENTA
    def test_existencias_cambian_antes_de_confirmar(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=6),
            1,
            self.usuario_autenticado
        )

        primera = ValidarInventarioVentaAPI(1, None, self.usuario_autenticado)
        self.assertTrue(primera["data"]["disponibilidad_suficiente"])

        # SIMULAR DISMINUCIÓN DE STOCK ANTES DE CONFIRMAR
        inventarioRepositorio.ActualizarCantidadInventarioRepositorio(1, 3)

        segunda = ValidarInventarioVentaAPI(1, None, self.usuario_autenticado)
        self.assertFalse(segunda["success"])
        self.assertFalse(segunda["data"]["disponibilidad_suficiente"])
        self.assertEqual(segunda["data"]["productos"][0]["existencias_disponibles"], 3)

    # CASO 6: PRODUCTO INEXISTENTE EN EL DETALLE
    def test_validar_inventario_producto_inexistente(self):
        datos = ValidarInventarioVentaSolicitud(
            productos=[
                {"producto_id": 999, "cantidad": 2}
            ]
        )

        respuesta = ValidarInventarioVentaAPI(1, datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El producto con ID 999 no existe")

    # VERIFICAR QUE EL ENDPOINT DE VALIDAR INVENTARIO ESTÉ EN OPENAPI / SWAGGER
    def test_documentacion_openapi_validar_inventario_venta(self):
        esquema = app.openapi()
        ruta = "/api/v1/ventas/{venta_id}/validar-inventario"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

    # VERIFICAR CONFIRMACIÓN COMPLETA CON confirmar=true, TOTALES, FECHA Y CONSULTA POSTERIOR
    def test_confirmar_venta_completo_con_totales_fecha_y_consulta(self):
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            1,
            self.usuario_autenticado
        )
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=2, cantidad=3),
            1,
            self.usuario_autenticado
        )

        # VALIDAR QUE confirmar=false SEA RECHAZADO
        respuesta_falsa = ConfirmarVentaAPI(
            1,
            ConfirmarVentaSolicitud(confirmar=False),
            self.usuario_autenticado
        )
        self.assertEqual(respuesta_falsa.status_code, 400)

        # CONFIRMAR CON confirmar=true
        respuesta = ConfirmarVentaAPI(
            1,
            ConfirmarVentaSolicitud(confirmar=True),
            self.usuario_autenticado
        )
        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["data"]["estado"], "confirmada")
        self.assertEqual(respuesta["data"]["cliente_id"], 1)
        self.assertEqual(respuesta["data"]["subtotal"], 26500.0)
        self.assertEqual(respuesta["data"]["total"], 26500.0)
        self.assertTrue(respuesta["data"]["inventario_actualizado"])
        self.assertIn("fecha_confirmacion", respuesta["data"])

        # CONSULTAR LA VENTA CONFIRMADA POR ID
        consulta = ObtenerVentaPorIdAPI(1, self.usuario_autenticado)
        self.assertTrue(consulta["success"])
        self.assertEqual(consulta["data"]["estado"], "confirmada")
        self.assertEqual(consulta["data"]["total"], 26500.0)


# PRUEBAS UNITARIAS PARA CONSULTAR Y LISTAR LAS VENTAS REGISTRADAS
class TestConsultaVentas(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "1234567890",
            "nombre": "Juan Perez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "9876543210",
            "nombre": "Maria Lopez",
            "telefono": "3009876543",
            "correo": "maria@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Arroz",
            "codigo": "PROD-001",
            "precio": 10000.0,
            "categoria_id": 1
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=1, cantidad_inicial=50),
            self.usuario_autenticado
        )

    def _crear_venta_confirmada(self, cliente_id: int, cantidad: int):
        venta = RegistrarVentaAPI(
            VentaRegistro(cliente_id=cliente_id),
            self.usuario_autenticado
        )["data"]
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=cantidad),
            venta["venta_id"],
            self.usuario_autenticado
        )
        ConfirmarVentaAPI(
            venta["venta_id"],
            ConfirmarVentaSolicitud(confirmar=True),
            self.usuario_autenticado
        )
        return venta["venta_id"]

    # CASO 1: CONSULTAR EL LISTADO DE VENTAS REGISTRADAS
    def test_consultar_listado_ventas_registradas(self):
        self._crear_venta_confirmada(1, 2)
        self._crear_venta_confirmada(2, 3)

        respuesta = ConsultarVentasAPI(usuario_autenticado=self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Consulta de ventas exitosa")
        self.assertEqual(len(respuesta["data"]), 2)
        self.assertEqual(respuesta["data"][0]["id_venta"], 1)
        self.assertEqual(respuesta["data"][0]["cliente"]["nombre"], "Juan Perez")
        self.assertEqual(respuesta["data"][0]["total"], 20000.0)
        self.assertEqual(respuesta["data"][1]["total"], 30000.0)

    # CASO 2: BUSCAR VENTAS POR NÚMERO, CLIENTE O FECHA
    def test_buscar_ventas_por_criterios(self):
        self._crear_venta_confirmada(1, 2)
        self._crear_venta_confirmada(2, 3)

        # BÚSQUEDA POR NÚMERO DE VENTA
        por_numero = ConsultarVentasAPI(
            numero_venta=2,
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(len(por_numero["data"]), 1)
        self.assertEqual(por_numero["data"][0]["cliente"]["nombre"], "Maria Lopez")

        # BÚSQUEDA POR CLIENTE
        por_cliente = ConsultarVentasAPI(
            cliente="Juan",
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(len(por_cliente["data"]), 1)
        self.assertEqual(por_cliente["data"][0]["id_venta"], 1)

        # BÚSQUEDA POR FECHA
        fecha_hoy = por_cliente["data"][0]["fecha"]
        por_fecha = ConsultarVentasAPI(
            fecha=fecha_hoy,
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(len(por_fecha["data"]), 2)

    # CASO 3: CONSULTAR EL DETALLE DE UNA VENTA
    def test_consultar_detalle_venta(self):
        venta_id = self._crear_venta_confirmada(1, 2)

        respuesta = ObtenerVentaPorIdAPI(venta_id, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Consulta de venta exitosa")
        self.assertEqual(respuesta["data"]["cliente"]["nombre"], "Juan Perez")
        self.assertEqual(respuesta["data"]["productos"][0]["nombre"], "Arroz")
        self.assertEqual(respuesta["data"]["productos"][0]["precio_unitario"], 10000.0)
        self.assertEqual(respuesta["data"]["productos"][0]["cantidad"], 2)
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 20000.0)
        self.assertEqual(respuesta["data"]["total"], 20000.0)

    # CASO 4: CONSULTAR VENTAS CUANDO NO EXISTEN REGISTROS
    def test_consultar_ventas_sin_registros(self):
        respuesta = ConsultarVentasAPI(usuario_autenticado=self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "No existen ventas registradas")
        self.assertEqual(respuesta["data"], [])

    # CASO 5: BUSCAR VENTAS SIN COINCIDENCIAS Y VALIDAR CRITERIOS INVÁLIDOS
    def test_buscar_ventas_sin_coincidencias_y_criterios_invalidos(self):
        self._crear_venta_confirmada(1, 2)

        sin_resultados = ConsultarVentasAPI(
            cliente="Inexistente",
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertTrue(sin_resultados["success"])
        self.assertEqual(
            sin_resultados["message"],
            "No se encontraron ventas con los criterios ingresados"
        )
        self.assertEqual(sin_resultados["data"], [])

        # FECHA INVÁLIDA Y CLIENTE 'string'
        fecha_invalida = ConsultarVentasAPI(
            fecha="25-10-2026",
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(fecha_invalida.status_code, 400)

        cliente_string = ConsultarVentasAPI(
            cliente="string",
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(cliente_string.status_code, 400)

    # CASO 6: CONSULTAR UNA VENTA INEXISTENTE
    def test_consultar_venta_inexistente(self):
        respuesta = ObtenerVentaPorIdAPI(999, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No se encontró la venta solicitada")

    # CASO 7: ERROR AL CONSULTAR LAS VENTAS
    @patch(
        "microservicios.ventas.repositorio.ventaRepositorio.ConsultarVentasRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_consultar_ventas(self, mock_consultar):
        respuesta = ConsultarVentasAPI(usuario_autenticado=self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible consultar las ventas")
        self.assertEqual(cuerpo["data"], [])

    # VERIFICAR QUE LOS ENDPOINTS DE CONSULTA ESTÉN EN OPENAPI / SWAGGER
    def test_documentacion_openapi_consulta_ventas(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/ventas/", esquema["paths"])
        self.assertIn("get", esquema["paths"]["/api/v1/ventas/"])
        self.assertIn("/api/v1/ventas/{venta_id}", esquema["paths"])
        self.assertIn("get", esquema["paths"]["/api/v1/ventas/{venta_id}"])


if __name__ == "__main__":
    unittest.main()
