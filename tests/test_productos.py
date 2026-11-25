import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.productos.api.dtos import ProductoRegistro
from microservicios.productos.api.productoApi import (
    ConsultarProductosAPI,
    RegistrarProductoAPI
)
from microservicios.productos.repositorio import productoRepositorio


# PRUEBAS UNITARIAS PARA EL REGISTRO DE PRODUCTOS
class TestRegistroProductos(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR UNA CATEGORÍA BASE PARA LAS PRUEBAS
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })

        # SIMULAR USUARIO SUPERADMINISTRADOR AUTENTICADO
        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: REGISTRO EXITOSO DE UN PRODUCTO Y VERIFICACIÓN EN EL LISTADO
    def test_registro_exitoso_producto(self):
        datos = ProductoRegistro(
            nombre="Arroz",
            codigo="PROD-001",
            precio=3500,
            categoria_id=1
        )

        respuesta = RegistrarProductoAPI(datos, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Producto registrado correctamente")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Arroz")
        self.assertEqual(respuesta["data"]["codigo"], "PROD-001")
        self.assertEqual(respuesta["data"]["precio"], 3500.0)
        self.assertEqual(respuesta["data"]["categoria_id"], 1)

        # VERIFICAR QUE EL PRODUCTO APARECE EN EL LISTADO DE PRODUCTOS REGISTRADOS
        listado = ConsultarProductosAPI(self.usuario_autenticado)
        self.assertTrue(listado["success"])
        self.assertEqual(len(listado["data"]), 1)
        self.assertEqual(listado["data"][0]["codigo"], "PROD-001")

    # CASO 2: CÓDIGO DE PRODUCTO DUPLICADO
    def test_codigo_producto_duplicado(self):
        datos_iniciales = ProductoRegistro(
            nombre="Arroz",
            codigo="PROD-001",
            precio=3500,
            categoria_id=1
        )
        RegistrarProductoAPI(datos_iniciales, self.usuario_autenticado)

        datos_duplicados = ProductoRegistro(
            nombre="Frijol",
            codigo="PROD-001",
            precio=4200,
            categoria_id=1
        )
        respuesta = RegistrarProductoAPI(datos_duplicados, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El código del producto ya se encuentra registrado")
        self.assertEqual(len(productoRepositorio.productos), 1)

    # CASO 3: DATOS OBLIGATORIOS INCOMPLETOS
    def test_datos_obligatorios_incompletos(self):
        with self.assertRaises(ValidationError) as contexto:
            ProductoRegistro(
                nombre="Arroz",
                codigo="PROD-002",
                precio=3500
            )

        errores = contexto.exception.errors()
        campos_con_error = [error["loc"][0] for error in errores]
        self.assertIn("categoria_id", campos_con_error)
        self.assertEqual(len(productoRepositorio.productos), 0)

    # CASO 4: PRECIO INVÁLIDO (NO NUMÉRICO O MENOR/IGUAL A CERO)
    def test_precio_invalido(self):
        with self.assertRaises(ValidationError):
            ProductoRegistro(
                nombre="Arroz",
                codigo="PROD-003",
                precio="no-numerico",
                categoria_id=1
            )

        with self.assertRaises(ValidationError):
            ProductoRegistro(
                nombre="Arroz",
                codigo="PROD-003",
                precio=-500,
                categoria_id=1
            )

        with self.assertRaises(ValidationError):
            ProductoRegistro(
                nombre="Arroz",
                codigo="PROD-003",
                precio=0,
                categoria_id=1
            )

        self.assertEqual(len(productoRepositorio.productos), 0)

    # CASO 5: CATEGORÍA INEXISTENTE
    def test_categoria_inexistente(self):
        datos = ProductoRegistro(
            nombre="Azúcar",
            codigo="PROD-004",
            precio=2800,
            categoria_id=999
        )

        respuesta = RegistrarProductoAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "La categoría seleccionada no existe")
        self.assertEqual(len(productoRepositorio.productos), 0)

    # CASO 6: ERROR INTERNO AL GUARDAR EL PRODUCTO
    @patch(
        "microservicios.productos.repositorio.productoRepositorio.RegistrarProductoRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_producto(self, mock_guardar):
        datos = ProductoRegistro(
            nombre="Aceite",
            codigo="PROD-005",
            precio=8500,
            categoria_id=1
        )

        respuesta = RegistrarProductoAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible registrar el producto")
        self.assertEqual(len(productoRepositorio.productos), 0)

    # VERIFICAR QUE EL ENDPOINT ESTÉ DOCUMENTADO EN OPENAPI / SWAGGER
    def test_documentacion_openapi_registrada(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/productos/", esquema["paths"])
        self.assertIn("post", esquema["paths"]["/api/v1/productos/"])
        self.assertIn("get", esquema["paths"]["/api/v1/productos/"])

    # VALIDAR QUE NO SE PERMITAN NÚMEROS EN EL NOMBRE NI PALABRAS COMO 'string' O CAMPOS VACÍOS
    def test_validaciones_estrictas_campos(self):
        # NOMBRE CON NÚMEROS
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz 123", codigo="PROD-010", precio=3500, categoria_id=1)

        # NOMBRE CON PALABRA POR DEFECTO 'string'
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="string", codigo="PROD-010", precio=3500, categoria_id=1)

        # NOMBRE VACÍO O CON SOLO ESPACIOS
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="   ", codigo="PROD-010", precio=3500, categoria_id=1)

        # CÓDIGO CON PALABRA POR DEFECTO 'string' O VACÍO O SOLO SÍMBOLOS
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="string", precio=3500, categoria_id=1)
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="   ", precio=3500, categoria_id=1)
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="---", precio=3500, categoria_id=1)

        # PRECIO CON 'string', BOOLEANO O VACÍO
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="PROD-010", precio="string", categoria_id=1)
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="PROD-010", precio=True, categoria_id=1)

        # CATEGORÍA CON BOOLEANO O STRING
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="PROD-010", precio=3500, categoria_id=True)
        with self.assertRaises(ValidationError):
            ProductoRegistro(nombre="Arroz", codigo="PROD-010", precio=3500, categoria_id="string")


if __name__ == "__main__":
    unittest.main()
