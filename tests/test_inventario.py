import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.inventario.api.dtos import ExistenciasInicialesRegistro
from microservicios.inventario.api.inventarioApi import RegistrarExistenciasInicialesAPI
from microservicios.inventario.repositorio import inventarioRepositorio
from microservicios.productos.repositorio import productoRepositorio


# PRUEBAS UNITARIAS PARA EL REGISTRO DE EXISTENCIAS INICIALES
class TestExistenciasIniciales(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR CATEGORÍA Y PRODUCTO BASE PARA LAS PRUEBAS
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

        # SIMULAR USUARIO SUPERADMINISTRADOR AUTENTICADO
        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: REGISTRO EXITOSO DE EXISTENCIAS INICIALES
    def test_registro_exitoso_existencias_iniciales(self):
        datos = ExistenciasInicialesRegistro(
            producto_id=1,
            cantidad_inicial=100
        )

        respuesta = RegistrarExistenciasInicialesAPI(datos, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "Existencias iniciales registradas correctamente"
        )
        self.assertEqual(respuesta["data"]["producto_id"], 1)
        self.assertEqual(respuesta["data"]["cantidad_inicial"], 100)
        self.assertEqual(len(inventarioRepositorio.inventarios), 1)

    # CASO 2: REGISTRO DE EXISTENCIAS CON CANTIDAD IGUAL A CERO
    def test_registro_existencias_cantidad_cero(self):
        datos = ExistenciasInicialesRegistro(
            producto_id=1,
            cantidad_inicial=0
        )

        respuesta = RegistrarExistenciasInicialesAPI(datos, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["data"]["producto_id"], 1)
        self.assertEqual(respuesta["data"]["cantidad_inicial"], 0)
        self.assertEqual(len(inventarioRepositorio.inventarios), 1)

    # CASO 3: REGISTRO CON CANTIDAD INVÁLIDA (NEGATIVA, DECIMAL, NO NUMÉRICA, 'string', BOOLEANO)
    def test_registro_cantidad_invalida(self):
        for valor_invalido in [-5, 10.5, "no-numerico", "string", True, None]:
            with self.assertRaises(ValidationError):
                ExistenciasInicialesRegistro(
                    producto_id=1,
                    cantidad_inicial=valor_invalido
                )

        # VALIDAR TAMBIÉN producto_id INVÁLIDO
        for producto_invalido in [0, -1, 1.5, "string", True, None]:
            with self.assertRaises(ValidationError):
                ExistenciasInicialesRegistro(
                    producto_id=producto_invalido,
                    cantidad_inicial=10
                )

        self.assertEqual(len(inventarioRepositorio.inventarios), 0)

    # CASO 4: REGISTRO PARA UN PRODUCTO INEXISTENTE
    def test_registro_producto_inexistente(self):
        datos = ExistenciasInicialesRegistro(
            producto_id=999,
            cantidad_inicial=50
        )

        respuesta = RegistrarExistenciasInicialesAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El producto seleccionado no existe")
        self.assertEqual(len(inventarioRepositorio.inventarios), 0)

    # CASO 5: ERROR AL GUARDAR LAS EXISTENCIAS INICIALES
    @patch(
        "microservicios.inventario.repositorio.inventarioRepositorio.RegistrarExistenciasInicialesRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_existencias(self, mock_guardar):
        datos = ExistenciasInicialesRegistro(
            producto_id=1,
            cantidad_inicial=100
        )

        respuesta = RegistrarExistenciasInicialesAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible registrar las existencias iniciales")
        self.assertEqual(len(inventarioRepositorio.inventarios), 0)

    # VERIFICAR QUE EL ENDPOINT ESTÉ DOCUMENTADO EN OPENAPI / SWAGGER
    def test_documentacion_openapi_inventario(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/inventario/existencias-iniciales", esquema["paths"])
        self.assertIn("post", esquema["paths"]["/api/v1/inventario/existencias-iniciales"])


if __name__ == "__main__":
    unittest.main()
