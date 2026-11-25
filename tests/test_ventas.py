import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.inventario.api.dtos import ExistenciasInicialesRegistro
from microservicios.inventario.api.inventarioApi import RegistrarExistenciasInicialesAPI
from microservicios.inventario.repositorio import inventarioRepositorio
from microservicios.inventario.servicio import inventarioServicio
from microservicios.productos.repositorio import productoRepositorio
from microservicios.ventas.api.dtos import ConfirmarVentaSolicitud, VentaRegistro
from microservicios.ventas.api.ventaApi import ConfirmarVentaAPI, RegistrarVentaAPI
from microservicios.ventas.repositorio import ventaRepositorio


# PRUEBAS UNITARIAS PARA CONFIRMAR VENTAS Y DESCONTAR EXISTENCIAS DEL INVENTARIO
class TestConfirmacionVentasInventario(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        ventaRepositorio.ventas.clear()
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR CATEGORÍA, PRODUCTOS Y EXISTENCIAS INICIALES
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
            VentaRegistro(productos=[
                {"producto_id": 1, "cantidad": 5},
                {"producto_id": 2, "cantidad": 3}
            ]),
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
            VentaRegistro(productos=[
                {"producto_id": 1, "cantidad": 5},
                {"producto_id": 2, "cantidad": 50}
            ]),
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
            VentaRegistro(productos=[{"producto_id": 1, "cantidad": 5}]),
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
            VentaRegistro(productos=[{"producto_id": 1, "cantidad": 5}]),
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
            VentaRegistro(productos=[
                {"producto_id": 1, "cantidad": 5},
                {"producto_id": 2, "cantidad": 3}
            ]),
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

        for valor_invalido in [0, -1, 1.5, "string", True, None]:
            with self.assertRaises(ValidationError):
                ConfirmarVentaSolicitud(venta_id=valor_invalido)

    # VERIFICAR QUE LOS ENDPOINTS DE VENTAS ESTÉN EN OPENAPI / SWAGGER
    def test_documentacion_openapi_ventas(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/ventas/", esquema["paths"])
        self.assertIn("/api/v1/ventas/{venta_id}/confirmar", esquema["paths"])
        self.assertIn("post", esquema["paths"]["/api/v1/ventas/{venta_id}/confirmar"])


if __name__ == "__main__":
    unittest.main()
