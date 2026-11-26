import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.inventario.api.dtos import (
    ExistenciasInicialesRegistro,
    ValidacionDisponibilidadSolicitud
)
from microservicios.inventario.api.inventarioApi import (
    ConsultarExistenciasProductoAPI,
    RegistrarExistenciasInicialesAPI,
    ValidarDisponibilidadAPI
)
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


# PRUEBAS UNITARIAS PARA LA CONSULTA DE EXISTENCIAS DISPONIBLES
class TestConsultaExistencias(unittest.TestCase):

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

    # CASO 1: CONSULTA EXITOSA DE EXISTENCIAS DISPONIBLES
    def test_consulta_exitosa_existencias(self):
        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=1, cantidad_inicial=100),
            self.usuario_autenticado
        )

        respuesta = ConsultarExistenciasProductoAPI(1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Consulta de existencias exitosa")
        self.assertEqual(respuesta["data"]["producto_id"], 1)
        self.assertEqual(respuesta["data"]["nombre_producto"], "Arroz")
        self.assertEqual(respuesta["data"]["codigo_producto"], "PROD-001")
        self.assertEqual(respuesta["data"]["cantidad_disponible"], 100)

    # CASO 2: CONSULTA DE UN PRODUCTO SIN EXISTENCIAS DISPONIBLES (CANTIDAD IGUAL A CERO)
    def test_consulta_producto_sin_existencias(self):
        RegistrarExistenciasInicialesAPI(
            ExistenciasInicialesRegistro(producto_id=1, cantidad_inicial=0),
            self.usuario_autenticado
        )

        respuesta = ConsultarExistenciasProductoAPI(1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "El producto no tiene existencias disponibles"
        )
        self.assertEqual(respuesta["data"]["producto_id"], 1)
        self.assertEqual(respuesta["data"]["cantidad_disponible"], 0)

    # CASO 3: CONSULTA DE UN PRODUCTO INEXISTENTE
    def test_consulta_existencias_producto_inexistente(self):
        respuesta = ConsultarExistenciasProductoAPI(999, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El producto seleccionado no existe")

    # CASO 4: ERROR DURANTE LA CONSULTA DE EXISTENCIAS
    @patch(
        "microservicios.inventario.repositorio.inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_consulta_existencias(self, mock_consulta):
        respuesta = ConsultarExistenciasProductoAPI(1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "No fue posible consultar las existencias del producto"
        )

    # VERIFICAR QUE EL ENDPOINT DE CONSULTA DE EXISTENCIAS ESTÉ EN OPENAPI / SWAGGER
    def test_documentacion_openapi_consulta_existencias(self):
        esquema = app.openapi()
        ruta = "/api/v1/inventario/productos/{producto_id}/existencias"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta])


# PRUEBAS UNITARIAS PARA LA VALIDACIÓN DE DISPONIBILIDAD ANTES DE UNA VENTA
class TestValidacionDisponibilidad(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        inventarioRepositorio.inventarios.clear()
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR CATEGORÍA, PRODUCTOS Y EXISTENCIAS BASE PARA LAS PRUEBAS
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

    # CASO 1: TODOS LOS PRODUCTOS TIENEN DISPONIBILIDAD SUFICIENTE
    def test_disponibilidad_suficiente_todos_los_productos(self):
        datos = ValidacionDisponibilidadSolicitud(
            productos=[
                {"producto_id": 1, "cantidad_solicitada": 5},
                {"producto_id": 2, "cantidad_solicitada": 3}
            ]
        )

        respuesta = ValidarDisponibilidadAPI(datos, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Validación de disponibilidad completada")
        self.assertTrue(respuesta["data"]["disponibilidad_suficiente"])
        self.assertEqual(len(respuesta["data"]["productos"]), 2)
        self.assertTrue(respuesta["data"]["productos"][0]["disponible"])
        self.assertTrue(respuesta["data"]["productos"][1]["disponible"])

    # CASO 2: UN PRODUCTO NO TIENE EXISTENCIAS SUFICIENTES Y NO SE DESCUENTA EL INVENTARIO
    def test_disponibilidad_insuficiente_sin_modificar_inventario(self):
        datos = ValidacionDisponibilidadSolicitud(
            productos=[
                {"producto_id": 1, "cantidad_solicitada": 5},
                {"producto_id": 2, "cantidad_solicitada": 50}
            ]
        )

        respuesta = ValidarDisponibilidadAPI(datos, self.usuario_autenticado)

        self.assertFalse(respuesta["success"])
        self.assertFalse(respuesta["data"]["disponibilidad_suficiente"])
        self.assertTrue(respuesta["data"]["productos"][0]["disponible"])
        self.assertFalse(respuesta["data"]["productos"][1]["disponible"])
        self.assertEqual(respuesta["data"]["productos"][1]["cantidad_solicitada"], 50)
        self.assertEqual(respuesta["data"]["productos"][1]["cantidad_disponible"], 20)

        # VERIFICAR QUE EL INVENTARIO NO FUE MODIFICADO
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(1)["cantidad_inicial"],
            100
        )
        self.assertEqual(
            inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio(2)["cantidad_inicial"],
            20
        )

    # CASO 3: EL USUARIO MODIFICA LA CANTIDAD SOLICITADA Y VUELVE A VALIDAR
    def test_modificar_cantidad_y_revalidar(self):
        datos_insuficientes = ValidacionDisponibilidadSolicitud(
            productos=[{"producto_id": 2, "cantidad_solicitada": 50}]
        )
        primera_respuesta = ValidarDisponibilidadAPI(
            datos_insuficientes,
            self.usuario_autenticado
        )
        self.assertFalse(primera_respuesta["data"]["disponibilidad_suficiente"])

        datos_corregidos = ValidacionDisponibilidadSolicitud(
            productos=[{"producto_id": 2, "cantidad_solicitada": 10}]
        )
        segunda_respuesta = ValidarDisponibilidadAPI(
            datos_corregidos,
            self.usuario_autenticado
        )
        self.assertTrue(segunda_respuesta["success"])
        self.assertTrue(segunda_respuesta["data"]["disponibilidad_suficiente"])

    # CASO 4: SE INTENTA VALIDAR UN PRODUCTO INEXISTENTE
    def test_validar_producto_inexistente(self):
        datos = ValidacionDisponibilidadSolicitud(
            productos=[{"producto_id": 999, "cantidad_solicitada": 5}]
        )

        respuesta = ValidarDisponibilidadAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El producto con ID 999 no existe")

    # CASO 5: ERROR DURANTE LA CONSULTA DE INVENTARIO
    @patch(
        "microservicios.inventario.repositorio.inventarioRepositorio.ObtenerInventarioPorProductoIdRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_validacion_disponibilidad(self, mock_consulta):
        datos = ValidacionDisponibilidadSolicitud(
            productos=[{"producto_id": 1, "cantidad_solicitada": 5}]
        )

        respuesta = ValidarDisponibilidadAPI(datos, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "No fue posible validar la disponibilidad de los productos"
        )

    # VALIDAR QUE NO SE PERMITAN CANTIDADES INVÁLIDAS NI LISTA VACÍA
    def test_validaciones_estrictas_disponibilidad(self):
        with self.assertRaises(ValidationError):
            ValidacionDisponibilidadSolicitud(productos=[])

        for cantidad_invalida in [0, -3, 2.5, "string", True, None]:
            with self.assertRaises(ValidationError):
                ValidacionDisponibilidadSolicitud(
                    productos=[{"producto_id": 1, "cantidad_solicitada": cantidad_invalida}]
                )

    # VERIFICAR QUE EL ENDPOINT DE VALIDACIÓN ESTÉ DOCUMENTADO EN OPENAPI / SWAGGER
    def test_documentacion_openapi_validacion_disponibilidad(self):
        esquema = app.openapi()
        ruta = "/api/v1/inventario/validar-disponibilidad"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])


if __name__ == "__main__":
    unittest.main()
