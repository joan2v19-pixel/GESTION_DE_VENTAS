import json
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from main import app
from microservicios.categorias.repositorio import categoriaRepositorio
from microservicios.productos.api.dtos import ProductoActualizar, ProductoRegistro
from microservicios.productos.api.productoApi import (
    ActualizarProductoAPI,
    BuscarProductosAPI,
    ConsultarProductosAPI,
    ObtenerProductoPorIdAPI,
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


# PRUEBAS UNITARIAS PARA LA CONSULTA Y LISTADO DE PRODUCTOS
class TestConsultaProductos(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR CATEGORÍAS BASE PARA LAS PRUEBAS
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Abarrotes",
            "descripcion": "Productos básicos de despensa"
        })

        # SIMULAR USUARIO SUPERADMINISTRADOR AUTENTICADO
        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: CONSULTA EXITOSA DE PRODUCTOS CON NOMBRE DE CATEGORÍA
    def test_consulta_exitosa_productos(self):
        RegistrarProductoAPI(
            ProductoRegistro(nombre="Arroz", codigo="PROD-001", precio=3500, categoria_id=1),
            self.usuario_autenticado
        )
        RegistrarProductoAPI(
            ProductoRegistro(nombre="Aceite", codigo="PROD-002", precio=6500, categoria_id=2),
            self.usuario_autenticado
        )

        respuesta = ConsultarProductosAPI(self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Consulta de productos exitosa")
        self.assertEqual(len(respuesta["data"]), 2)
        self.assertEqual(respuesta["data"][0]["nombre"], "Arroz")
        self.assertEqual(respuesta["data"][0]["codigo"], "PROD-001")
        self.assertEqual(respuesta["data"][0]["precio"], 3500.0)
        self.assertEqual(respuesta["data"][0]["categoria"], "Granos")
        self.assertEqual(respuesta["data"][1]["categoria"], "Abarrotes")

    # CASO 2: NO EXISTEN PRODUCTOS REGISTRADOS
    def test_consulta_sin_productos_registrados(self):
        respuesta = ConsultarProductosAPI(self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "No existen productos registrados")
        self.assertEqual(respuesta["data"], [])

    # CASO 3: ERROR DURANTE LA CONSULTA DE PRODUCTOS (INCLUIDO ERROR DE CONEXIÓN)
    @patch(
        "microservicios.productos.repositorio.productoRepositorio.ConsultarProductosRepositorio",
        side_effect=ConnectionError("Sin conexión con el servidor")
    )
    def test_error_durante_consulta_productos(self, mock_consultar):
        respuesta = ConsultarProductosAPI(self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible consultar los productos")
        self.assertEqual(cuerpo["data"], [])

    # CASO 4: CONSULTA DEL DETALLE DE UN PRODUCTO
    def test_consulta_detalle_producto(self):
        RegistrarProductoAPI(
            ProductoRegistro(nombre="Arroz", codigo="PROD-001", precio=3500, categoria_id=1),
            self.usuario_autenticado
        )

        respuesta = ObtenerProductoPorIdAPI(1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Consulta de producto exitosa")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Arroz")
        self.assertEqual(respuesta["data"]["codigo"], "PROD-001")
        self.assertEqual(respuesta["data"]["precio"], 3500.0)
        self.assertEqual(respuesta["data"]["categoria"], "Granos")

    # CASO 5: CONSULTA DE PRODUCTO INEXISTENTE
    def test_consulta_producto_inexistente(self):
        respuesta = ObtenerProductoPorIdAPI(999, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No se encontró el producto solicitado")


# PRUEBAS UNITARIAS PARA LA BÚSQUEDA DE PRODUCTOS POR NOMBRE O CÓDIGO
class TestBusquedaProductos(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR CATEGORÍA Y PRODUCTOS BASE PARA LAS PRUEBAS
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarProductoAPI(
            ProductoRegistro(nombre="Arroz", codigo="PROD-001", precio=3500, categoria_id=1),
            self.usuario_autenticado
        )
        RegistrarProductoAPI(
            ProductoRegistro(nombre="Frijol", codigo="PROD-002", precio=4200, categoria_id=1),
            self.usuario_autenticado
        )

    # CASO 1: BÚSQUEDA EXITOSA POR NOMBRE
    def test_busqueda_exitosa_por_nombre(self):
        respuesta = BuscarProductosAPI(
            nombre="Arroz",
            codigo=None,
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Búsqueda de productos exitosa")
        self.assertEqual(len(respuesta["data"]), 1)
        self.assertEqual(respuesta["data"][0]["nombre"], "Arroz")
        self.assertEqual(respuesta["data"][0]["codigo"], "PROD-001")
        self.assertEqual(respuesta["data"][0]["categoria"], "Granos")

    # CASO 2: BÚSQUEDA EXITOSA POR CÓDIGO
    def test_busqueda_exitosa_por_codigo(self):
        respuesta = BuscarProductosAPI(
            nombre=None,
            codigo="PROD-002",
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Búsqueda de productos exitosa")
        self.assertEqual(len(respuesta["data"]), 1)
        self.assertEqual(respuesta["data"][0]["nombre"], "Frijol")
        self.assertEqual(respuesta["data"][0]["codigo"], "PROD-002")

    # CASO 3: BÚSQUEDA SIN COINCIDENCIAS
    def test_busqueda_sin_coincidencias(self):
        respuesta = BuscarProductosAPI(
            nombre="Lenteja",
            codigo=None,
            usuario_autenticado=self.usuario_autenticado
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "No se encontraron productos con el criterio de búsqueda ingresado"
        )
        self.assertEqual(respuesta["data"], [])

    # CASO 4: CRITERIO DE BÚSQUEDA VACÍO O INVÁLIDO
    def test_criterio_busqueda_vacio_o_invalido(self):
        respuesta_vacia = BuscarProductosAPI(
            nombre="   ",
            codigo=None,
            usuario_autenticado=self.usuario_autenticado
        )
        cuerpo_vacio = json.loads(respuesta_vacia.body.decode("utf-8"))

        self.assertEqual(respuesta_vacia.status_code, 400)
        self.assertFalse(cuerpo_vacio["success"])
        self.assertEqual(
            cuerpo_vacio["message"],
            "Debe ingresar al menos un criterio de búsqueda (nombre o código)"
        )

        # VALIDAR RECHAZO DE 'string' Y NÚMEROS EN EL CRITERIO NOMBRE
        respuesta_string = BuscarProductosAPI(
            nombre="string",
            codigo=None,
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(respuesta_string.status_code, 400)

        respuesta_numeros = BuscarProductosAPI(
            nombre="Arroz123",
            codigo=None,
            usuario_autenticado=self.usuario_autenticado
        )
        self.assertEqual(respuesta_numeros.status_code, 400)

    # CASO 5: ERROR DURANTE LA BÚSQUEDA
    @patch(
        "microservicios.productos.repositorio.productoRepositorio.BuscarProductosRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_busqueda(self, mock_buscar):
        respuesta = BuscarProductosAPI(
            nombre="Arroz",
            codigo=None,
            usuario_autenticado=self.usuario_autenticado
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible realizar la búsqueda de productos")
        self.assertEqual(cuerpo["data"], [])

    # VERIFICAR QUE EL ENDPOINT DE BÚSQUEDA ESTÉ REGISTRADO EN OPENAPI / SWAGGER
    def test_documentacion_openapi_busqueda(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/productos/buscar", esquema["paths"])
        self.assertIn("get", esquema["paths"]["/api/v1/productos/buscar"])


# PRUEBAS UNITARIAS PARA LA ACTUALIZACIÓN DE PRODUCTOS
class TestActualizacionProductos(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        productoRepositorio.productos.clear()
        categoriaRepositorio.categorias.clear()

        # REGISTRAR CATEGORÍAS Y PRODUCTOS BASE PARA LAS PRUEBAS
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Granos",
            "descripcion": "Productos de granos y cereales"
        })
        categoriaRepositorio.RegistrarCategoriaRepositorio({
            "nombre": "Abarrotes",
            "descripcion": "Productos básicos de despensa"
        })

        self.usuario_autenticado = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarProductoAPI(
            ProductoRegistro(nombre="Arroz", codigo="PROD-001", precio=3500, categoria_id=1),
            self.usuario_autenticado
        )
        RegistrarProductoAPI(
            ProductoRegistro(nombre="Aceite", codigo="PROD-002", precio=6500, categoria_id=2),
            self.usuario_autenticado
        )

    # CASO 1: ACTUALIZACIÓN EXITOSA DE UN PRODUCTO
    def test_actualizacion_exitosa_producto(self):
        datos = ProductoActualizar(
            nombre="Arroz Blanco",
            codigo="PROD-001",
            precio=3800,
            categoria_id=2
        )

        respuesta = ActualizarProductoAPI(datos, 1, self.usuario_autenticado)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Producto actualizado correctamente")
        self.assertEqual(respuesta["data"]["nombre"], "Arroz Blanco")
        self.assertEqual(respuesta["data"]["precio"], 3800.0)
        self.assertEqual(respuesta["data"]["categoria"], "Abarrotes")

        # VERIFICAR AL CONSULTAR EL PRODUCTO
        consulta = ObtenerProductoPorIdAPI(1, self.usuario_autenticado)
        self.assertEqual(consulta["data"]["nombre"], "Arroz Blanco")
        self.assertEqual(consulta["data"]["precio"], 3800.0)

    # CASO 2: PRODUCTO INEXISTENTE
    def test_actualizacion_producto_inexistente(self):
        datos = ProductoActualizar(
            nombre="Arroz",
            codigo="PROD-099",
            precio=3800,
            categoria_id=1
        )

        respuesta = ActualizarProductoAPI(datos, 999, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "El producto seleccionado no existe")

    # CASO 3: DATOS OBLIGATORIOS INCOMPLETOS
    def test_actualizacion_datos_incompletos(self):
        with self.assertRaises(ValidationError) as contexto:
            ProductoActualizar(
                nombre="Arroz",
                codigo="PROD-001",
                precio=3800
            )

        campos = [error["loc"][0] for error in contexto.exception.errors()]
        self.assertIn("categoria_id", campos)
        self.assertEqual(productoRepositorio.ObtenerProductoPorIdRepositorio(1)["precio"], 3500.0)

    # CASO 4: CÓDIGO DUPLICADO EN OTRO PRODUCTO
    def test_actualizacion_codigo_duplicado(self):
        datos = ProductoActualizar(
            nombre="Arroz",
            codigo="PROD-002",
            precio=3800,
            categoria_id=1
        )

        respuesta = ActualizarProductoAPI(datos, 1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 409)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(
            cuerpo["message"],
            "El código del producto ya se encuentra registrado en otro producto"
        )
        self.assertEqual(productoRepositorio.ObtenerProductoPorIdRepositorio(1)["codigo"], "PROD-001")

    # CASO 5: PRECIO INVÁLIDO
    def test_actualizacion_precio_invalido(self):
        with self.assertRaises(ValidationError):
            ProductoActualizar(
                nombre="Arroz",
                codigo="PROD-001",
                precio="string",
                categoria_id=1
            )

        with self.assertRaises(ValidationError):
            ProductoActualizar(
                nombre="Arroz",
                codigo="PROD-001",
                precio=-100,
                categoria_id=1
            )

        self.assertEqual(productoRepositorio.ObtenerProductoPorIdRepositorio(1)["precio"], 3500.0)

    # CASO 6: CATEGORÍA INEXISTENTE
    def test_actualizacion_categoria_inexistente(self):
        datos = ProductoActualizar(
            nombre="Arroz",
            codigo="PROD-001",
            precio=3800,
            categoria_id=999
        )

        respuesta = ActualizarProductoAPI(datos, 1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 404)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "La categoría seleccionada no existe")
        self.assertEqual(productoRepositorio.ObtenerProductoPorIdRepositorio(1)["categoria_id"], 1)

    # CASO 7: ERROR AL GUARDAR LOS CAMBIOS
    @patch(
        "microservicios.productos.repositorio.productoRepositorio.ActualizarProductoRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_actualizar_producto(self, mock_actualizar):
        datos = ProductoActualizar(
            nombre="Arroz Nuevo",
            codigo="PROD-001",
            precio=3900,
            categoria_id=1
        )

        respuesta = ActualizarProductoAPI(datos, 1, self.usuario_autenticado)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible actualizar el producto")
        self.assertEqual(productoRepositorio.ObtenerProductoPorIdRepositorio(1)["nombre"], "Arroz")

    # VERIFICAR QUE EL ENDPOINT PUT ESTÉ REGISTRADO EN OPENAPI / SWAGGER
    def test_documentacion_openapi_actualizacion(self):
        esquema = app.openapi()
        self.assertIn("/api/v1/productos/{id}", esquema["paths"])
        self.assertIn("put", esquema["paths"]["/api/v1/productos/{id}"])


if __name__ == "__main__":
    unittest.main()
