import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.clientes.repositorio import clienteRepositorio
from microservicios.comprobantes.api.comprobanteApi import (
    ConsultarComprobantesAPI,
    GenerarComprobanteAPI,
    ObtenerComprobantePorIdAPI
)
from microservicios.comprobantes.api.dtos import ComprobanteRegistro
from microservicios.comprobantes.repositorio import comprobanteRepositorio
from microservicios.inventario.api.dtos import ExistenciasInicialesRegistro
from microservicios.inventario.api.inventarioApi import RegistrarExistenciasInicialesAPI
from microservicios.inventario.repositorio import inventarioRepositorio
from microservicios.productos.repositorio import productoRepositorio
from microservicios.ventas.api.dtos import (
    ConfirmarVentaSolicitud,
    DetalleVentaAgregar,
    VentaRegistro
)
from microservicios.ventas.api.ventaApi import (
    AgregarDetalleVentaAPI,
    ConfirmarVentaAPI,
    RegistrarVentaAPI
)
from microservicios.ventas.repositorio import ventaRepositorio


# PRUEBAS UNITARIAS PARA GENERAR COMPROBANTES DE VENTAS CONFIRMADAS
class TestComprobantes(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        comprobanteRepositorio.comprobantes.clear()
        ventaRepositorio.ventas.clear()
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "123456789",
            "nombre": "Juan Pérez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Producto A",
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

    def _crear_y_confirmar_venta(self) -> int:
        venta = RegistrarVentaAPI(
            VentaRegistro(cliente_id=1),
            self.usuario_autenticado
        )["data"]
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            venta["venta_id"],
            self.usuario_autenticado
        )
        ConfirmarVentaAPI(
            venta["venta_id"],
            ConfirmarVentaSolicitud(confirmar=True),
            self.usuario_autenticado
        )
        return venta["venta_id"]

    # CASO 1: GENERACIÓN EXITOSA DEL COMPROBANTE
    def test_generacion_exitosa_comprobante(self):
        venta_id = self._crear_y_confirmar_venta()

        respuesta = GenerarComprobanteAPI(
            ComprobanteRegistro(venta_id=venta_id),
            self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Comprobante generado correctamente")
        self.assertEqual(respuesta["data"]["comprobante_id"], 1)
        self.assertEqual(respuesta["data"]["venta_id"], venta_id)
        self.assertEqual(respuesta["data"]["cliente"]["nombre"], "Juan Pérez")
        self.assertEqual(respuesta["data"]["cliente"]["identificacion"], "123456789")
        self.assertEqual(respuesta["data"]["productos"][0]["nombre"], "Producto A")
        self.assertEqual(respuesta["data"]["productos"][0]["cantidad"], 2)
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 20000.0)
        self.assertEqual(respuesta["data"]["total"], 20000.0)

        # VERIFICAR QUE SE PUEDE CONSULTAR POSTERIORMENTE
        consulta = ObtenerComprobantePorIdAPI(1, self.usuario_autenticado)
        self.assertTrue(consulta["success"])
        self.assertEqual(consulta["data"]["venta_id"], venta_id)

    # CASO 2: VENTA INEXISTENTE
    def test_comprobante_venta_inexistente(self):
        respuesta = GenerarComprobanteAPI(
            ComprobanteRegistro(venta_id=999),
            self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "La venta seleccionada no existe")
        self.assertEqual(len(comprobanteRepositorio.comprobantes), 0)

    # CASO 3: VENTA SIN CONFIRMAR
    def test_comprobante_venta_sin_confirmar(self):
        venta = RegistrarVentaAPI(
            VentaRegistro(cliente_id=1),
            self.usuario_autenticado
        )["data"]
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            venta["venta_id"],
            self.usuario_autenticado
        )

        respuesta = GenerarComprobanteAPI(
            ComprobanteRegistro(venta_id=venta["venta_id"]),
            self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "La venta debe estar confirmada para generar el comprobante"
        )
        self.assertEqual(len(comprobanteRepositorio.comprobantes), 0)

    # CASO 4: INFORMACIÓN INCOMPLETA PARA GENERAR EL COMPROBANTE
    def test_comprobante_informacion_incompleta(self):
        venta_id = self._crear_y_confirmar_venta()

        # SIMULAR QUE EL CLIENTE NO TIENE IDENTIFICACIÓN COMPLETA
        clienteRepositorio.ObtenerClientePorIdRepositorio(1)["identificacion"] = ""

        respuesta = GenerarComprobanteAPI(
            ComprobanteRegistro(venta_id=venta_id),
            self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertIn("Faltan datos del cliente", cuerpo["message"])
        self.assertEqual(len(comprobanteRepositorio.comprobantes), 0)

    # CASO 5: ERROR AL GUARDAR EL COMPROBANTE
    @patch(
        "microservicios.comprobantes.repositorio.comprobanteRepositorio.RegistrarComprobanteRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_comprobante(self, mock_guardar):
        venta_id = self._crear_y_confirmar_venta()

        respuesta = GenerarComprobanteAPI(
            ComprobanteRegistro(venta_id=venta_id),
            self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible generar el comprobante")
        self.assertEqual(len(comprobanteRepositorio.comprobantes), 0)

    # VALIDAR DTO ESTRICTO Y DOCUMENTACIÓN OPENAPI / SWAGGER
    def test_validaciones_dto_y_openapi_comprobantes(self):
        for valor_invalido in [0, -1, 1.5, "string", True, None]:
            with self.assertRaises(ValidationError):
                ComprobanteRegistro(venta_id=valor_invalido)

        listado = ConsultarComprobantesAPI(self.usuario_autenticado)
        self.assertTrue(listado["success"])
        self.assertEqual(listado["data"], [])

        esquema = app.openapi()
        self.assertIn("/api/v1/comprobantes/", esquema["paths"])
        self.assertIn("post", esquema["paths"]["/api/v1/comprobantes/"])
        self.assertIn("get", esquema["paths"]["/api/v1/comprobantes/"])
        self.assertIn("/api/v1/comprobantes/{comprobante_id}", esquema["paths"])


# PRUEBAS UNITARIAS PARA CONSULTAR LOS DATOS DE UN COMPROBANTE DE VENTA
class TestConsultaComprobante(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        comprobanteRepositorio.comprobantes.clear()
        ventaRepositorio.ventas.clear()
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()
        clienteRepositorio.clientes.clear()

        clienteRepositorio.RegistrarClienteRepositorio({
            "identificacion": "123456789",
            "nombre": "Juan Pérez",
            "telefono": "3001234567",
            "correo": "juan@ejemplo.com"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        productoRepositorio.RegistrarProductoRepositorio({
            "nombre": "Producto A",
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

        venta = RegistrarVentaAPI(
            VentaRegistro(cliente_id=1),
            self.usuario_autenticado
        )["data"]
        AgregarDetalleVentaAPI(
            DetalleVentaAgregar(producto_id=1, cantidad=2),
            venta["venta_id"],
            self.usuario_autenticado
        )
        ConfirmarVentaAPI(
            venta["venta_id"],
            ConfirmarVentaSolicitud(confirmar=True),
            self.usuario_autenticado
        )
        GenerarComprobanteAPI(
            ComprobanteRegistro(venta_id=venta["venta_id"]),
            self.usuario_autenticado
        )

    # CASO 1 Y CASO 4: CONSULTA EXITOSA Y VERIFICACIÓN SIN MODIFICAR LOS DATOS
    def test_consulta_exitosa_y_verificacion_comprobante(self):
        respuesta = ObtenerComprobantePorIdAPI(1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Consulta del comprobante exitosa")
        self.assertEqual(respuesta["data"]["comprobante_id"], 1)
        self.assertEqual(respuesta["data"]["venta_id"], 1)
        self.assertEqual(respuesta["data"]["cliente"]["nombre"], "Juan Pérez")
        self.assertEqual(respuesta["data"]["cliente"]["identificacion"], "123456789")
        self.assertEqual(respuesta["data"]["productos"][0]["nombre"], "Producto A")
        self.assertEqual(respuesta["data"]["productos"][0]["cantidad"], 2)
        self.assertEqual(respuesta["data"]["productos"][0]["subtotal"], 20000.0)
        self.assertEqual(respuesta["data"]["total"], 20000.0)

        # VERIFICAR QUE LA CONSULTA NO MODIFICÓ LOS DATOS ALMACENADOS
        almacenado = comprobanteRepositorio.ObtenerComprobantePorIdRepositorio(1)
        self.assertEqual(almacenado["total"], 20000.0)
        self.assertEqual(almacenado["productos"][0]["cantidad"], 2)

    # CASO 2: COMPROBANTE INEXISTENTE
    def test_consulta_comprobante_inexistente(self):
        respuesta = ObtenerComprobantePorIdAPI(999, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No se encontró el comprobante solicitado")

    # CASO 3: ERROR DURANTE LA CONSULTA
    @patch(
        "microservicios.comprobantes.repositorio.comprobanteRepositorio.ObtenerComprobantePorIdRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_consulta_comprobante(self, mock_consulta):
        respuesta = ObtenerComprobantePorIdAPI(1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible consultar el comprobante")

    # VERIFICAR DOCUMENTACIÓN OPENAPI DE GET /api/v1/comprobantes/{comprobante_id}
    def test_documentacion_openapi_consulta_comprobante(self):
        esquema = app.openapi()
        ruta = "/api/v1/comprobantes/{comprobante_id}"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta])


if __name__ == "__main__":
    unittest.main()
