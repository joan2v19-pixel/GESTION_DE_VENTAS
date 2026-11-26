import copy
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

from main import app
from microservicios.categorias.api.categoriaApi import (
    ActualizarCategoriaAPI,
    ConsultarCategoriasAPI,
    ObtenerCategoriaPorIdAPI,
    RegistrarCategoriaAPI
)
from microservicios.categorias.api.dtos import (
    CategoriaActualizar,
    CategoriaRegistro
)
from microservicios.categorias.repositorio import categoriaRepositorio


# PRUEBAS UNITARIAS PARA EL REGISTRO DE CATEGORÍAS DE PRODUCTOS
class TestRegistroCategorias(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        categoriaRepositorio.categorias.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1 Y 2: REGISTRO EXITOSO DE UNA CATEGORÍA CON DESCRIPCIÓN Y CONSULTA POSTERIOR
    def test_registro_exitoso_categoria_y_consulta(self):
        datos = CategoriaRegistro(
            nombre="Accesorios",
            descripcion="Categoría para productos accesorios"
        )

        respuesta = RegistrarCategoriaAPI(datos, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CATEGORÍA REGISTRADA EXITOSAMENTE.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Accesorios")
        self.assertEqual(
            respuesta["data"]["descripcion"],
            "Categoría para productos accesorios"
        )

        # VERIFICAR CONSULTA POSTERIOR
        listado = ConsultarCategoriasAPI(self.superadministrador)
        self.assertTrue(listado["success"])
        self.assertEqual(len(listado["data"]), 1)

        detalle = ObtenerCategoriaPorIdAPI(1, self.superadministrador)
        self.assertTrue(detalle["success"])
        self.assertEqual(detalle["data"]["nombre"], "Accesorios")

    # CASO 3: REGISTRO SIN NOMBRE O CON CAMPOS OBLIGATORIOS VACÍOS
    def test_registro_categoria_sin_nombre_o_campos_vacios(self):
        with self.assertRaises(ValidationError) as contexto:
            CategoriaRegistro(
                descripcion="Categoría para productos accesorios"
            )

        campos = [error["loc"][0] for error in contexto.exception.errors()]
        self.assertIn("nombre", campos)

        with self.assertRaises(ValidationError):
            CategoriaRegistro(
                nombre="   ",
                descripcion="   "
            )

        self.assertEqual(len(categoriaRepositorio.categorias), 0)

    # CASO 4: REGISTRO DE UNA CATEGORÍA DUPLICADA
    def test_registro_categoria_duplicada(self):
        RegistrarCategoriaAPI(
            CategoriaRegistro(
                nombre="Accesorios",
                descripcion="Categoría para productos accesorios"
            ),
            self.superadministrador
        )

        with self.assertRaises(HTTPException) as contexto:
            RegistrarCategoriaAPI(
                CategoriaRegistro(
                    nombre="accesorios",
                    descripcion="Otra descripción válida"
                ),
                self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 409)
        self.assertEqual(
            contexto.exception.detail,
            "LA CATEGORÍA YA SE ENCUENTRA REGISTRADA."
        )
        self.assertEqual(len(categoriaRepositorio.categorias), 1)

    # VALIDAR FORMATO INVÁLIDO EN NOMBRE
    def test_registro_categoria_formato_invalido(self):
        with self.assertRaises(ValidationError):
            CategoriaRegistro(
                nombre="Accesorios @#$",
                descripcion="Categoría para productos accesorios"
            )

        self.assertEqual(len(categoriaRepositorio.categorias), 0)

    # CASO 5: ERROR AL GUARDAR LA CATEGORÍA
    @patch(
        "microservicios.categorias.repositorio.categoriaRepositorio.RegistrarCategoriaRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_categoria(self, mock_guardar):
        datos = CategoriaRegistro(
            nombre="Accesorios",
            descripcion="Categoría para productos accesorios"
        )

        with self.assertRaises(HTTPException) as contexto:
            RegistrarCategoriaAPI(datos, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE REGISTRAR LA CATEGORÍA."
        )
        self.assertEqual(len(categoriaRepositorio.categorias), 0)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE REGISTRO DE CATEGORÍAS
    def test_documentacion_openapi_registro_categorias(self):
        esquema = app.openapi()
        ruta = "/api/v1/categorias/"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

        post_doc = esquema["paths"][ruta]["post"]
        self.assertIn("summary", post_doc)
        self.assertIn("description", post_doc)
        for codigo in ["201", "400", "409", "500"]:
            self.assertIn(codigo, post_doc["responses"])


# PRUEBAS UNITARIAS PARA CONSULTAR Y LISTAR CATEGORÍAS
class TestConsultaCategorias(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        categoriaRepositorio.categorias.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: CONSULTAR CATEGORÍAS REGISTRADAS
    def test_consulta_categorias_registradas(self):
        RegistrarCategoriaAPI(
            CategoriaRegistro(
                nombre="Accesorios",
                descripcion="Categoría para productos accesorios"
            ),
            self.superadministrador
        )
        RegistrarCategoriaAPI(
            CategoriaRegistro(
                nombre="Repuestos",
                descripcion="Categoría para repuestos"
            ),
            self.superadministrador
        )

        respuesta = ConsultarCategoriasAPI(self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CONSULTA DE CATEGORÍAS EXITOSA.")
        self.assertEqual(len(respuesta["data"]), 2)
        self.assertEqual(respuesta["data"][0]["nombre"], "Accesorios")
        self.assertEqual(respuesta["data"][1]["nombre"], "Repuestos")

    # CASO 2: CONSULTAR CUANDO NO EXISTEN CATEGORÍAS REGISTRADAS
    def test_consulta_sin_categorias_registradas(self):
        respuesta = ConsultarCategoriasAPI(self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "NO EXISTEN CATEGORÍAS REGISTRADAS.")
        self.assertEqual(respuesta["data"], [])

    # CASO 3: CONSULTAR UNA CATEGORÍA ESPECÍFICA SIN MODIFICAR DATOS
    def test_consulta_categoria_por_id_sin_modificar(self):
        RegistrarCategoriaAPI(
            CategoriaRegistro(
                nombre="Accesorios",
                descripcion="Categoría para productos accesorios"
            ),
            self.superadministrador
        )

        estado_antes = copy.deepcopy(categoriaRepositorio.categorias)
        respuesta = ObtenerCategoriaPorIdAPI(1, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CONSULTA DE CATEGORÍA EXITOSA.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Accesorios")
        self.assertEqual(
            respuesta["data"]["descripcion"],
            "Categoría para productos accesorios"
        )
        self.assertEqual(estado_antes, categoriaRepositorio.categorias)

    # CONSULTAR UNA CATEGORÍA INEXISTENTE
    def test_consulta_categoria_inexistente(self):
        with self.assertRaises(HTTPException) as contexto:
            ObtenerCategoriaPorIdAPI(999, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "NO SE ENCONTRÓ LA CATEGORÍA SOLICITADA."
        )

    # ERROR DURANTE LA CONSULTA DE CATEGORÍAS
    @patch(
        "microservicios.categorias.repositorio.categoriaRepositorio.ConsultarCategoriasRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_listado_categorias(self, mock_consulta):
        with self.assertRaises(HTTPException) as contexto:
            ConsultarCategoriasAPI(self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR LAS CATEGORÍAS."
        )

    @patch(
        "microservicios.categorias.repositorio.categoriaRepositorio.ObtenerCategoriaPorIdRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_detalle_categoria(self, mock_detalle):
        with self.assertRaises(HTTPException) as contexto:
            ObtenerCategoriaPorIdAPI(1, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR LA CATEGORÍA."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DE LOS ENDPOINTS DE CONSULTA DE CATEGORÍAS
    def test_documentacion_openapi_consulta_categorias(self):
        esquema = app.openapi()

        ruta_lista = "/api/v1/categorias/"
        self.assertIn(ruta_lista, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta_lista])
        get_lista = esquema["paths"][ruta_lista]["get"]
        self.assertIn("summary", get_lista)
        self.assertIn("description", get_lista)
        self.assertIn("200", get_lista["responses"])
        self.assertIn("500", get_lista["responses"])

        ruta_detalle = "/api/v1/categorias/{id}"
        self.assertIn(ruta_detalle, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta_detalle])
        get_detalle = esquema["paths"][ruta_detalle]["get"]
        self.assertIn("summary", get_detalle)
        self.assertIn("description", get_detalle)
        for codigo in ["200", "404", "500"]:
            self.assertIn(codigo, get_detalle["responses"])


# PRUEBAS UNITARIAS PARA ACTUALIZAR INFORMACIÓN DE CATEGORÍAS
class TestActualizacionCategorias(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        categoriaRepositorio.categorias.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarCategoriaAPI(
            CategoriaRegistro(
                nombre="Accesorios",
                descripcion="Categoría para productos accesorios"
            ),
            self.superadministrador
        )
        RegistrarCategoriaAPI(
            CategoriaRegistro(
                nombre="Repuestos",
                descripcion="Categoría para repuestos"
            ),
            self.superadministrador
        )

    # CASO 1: ACTUALIZACIÓN EXITOSA DE UNA CATEGORÍA Y VERIFICACIÓN POSTERIOR
    def test_actualizacion_exitosa_categoria(self):
        datos = CategoriaActualizar(
            nombre="Bebidas",
            descripcion="Productos líquidos para consumo"
        )

        respuesta = ActualizarCategoriaAPI(
            id=1,
            datos=datos,
            usuario_autenticado=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CATEGORÍA ACTUALIZADA CORRECTAMENTE.")

        consulta = ObtenerCategoriaPorIdAPI(1, self.superadministrador)
        self.assertEqual(consulta["data"]["nombre"], "Bebidas")
        self.assertEqual(
            consulta["data"]["descripcion"],
            "Productos líquidos para consumo"
        )

    # CASO 2: ACTUALIZACIÓN DE UNA CATEGORÍA INEXISTENTE
    def test_actualizacion_categoria_inexistente(self):
        datos = CategoriaActualizar(
            nombre="Bebidas",
            descripcion="Productos líquidos para consumo"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarCategoriaAPI(
                id=999,
                datos=datos,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "LA CATEGORÍA SELECCIONADA NO EXISTE."
        )

    # CASO 3 Y 4: DATOS OBLIGATORIOS INCOMPLETOS O INFORMACIÓN NO VÁLIDA
    def test_actualizacion_campos_incompletos_o_invalidos(self):
        with self.assertRaises(ValidationError):
            CategoriaActualizar(
                descripcion="Productos líquidos para consumo"
            )

        with self.assertRaises(ValidationError):
            CategoriaActualizar(
                nombre="   ",
                descripcion="   "
            )

        with self.assertRaises(ValidationError):
            CategoriaActualizar(
                nombre="Bebidas @#$",
                descripcion="Productos líquidos para consumo"
            )

        self.assertEqual(
            categoriaRepositorio.ObtenerCategoriaPorIdRepositorio(1)["nombre"],
            "Accesorios"
        )

    # NOMBRE DUPLICADO EN OTRA CATEGORÍA
    def test_actualizacion_nombre_duplicado(self):
        datos = CategoriaActualizar(
            nombre="repuestos",
            descripcion="Nueva descripción válida"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarCategoriaAPI(
                id=1,
                datos=datos,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 409)
        self.assertEqual(
            contexto.exception.detail,
            "EL NOMBRE YA SE ENCUENTRA REGISTRADO EN OTRA CATEGORÍA."
        )
        self.assertEqual(
            categoriaRepositorio.ObtenerCategoriaPorIdRepositorio(1)["nombre"],
            "Accesorios"
        )

    # CASO 5: ERROR AL GUARDAR LOS CAMBIOS DE LA CATEGORÍA
    @patch(
        "microservicios.categorias.repositorio.categoriaRepositorio.ActualizarCategoriaRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_actualizar_categoria(self, mock_actualizar):
        datos = CategoriaActualizar(
            nombre="Bebidas",
            descripcion="Productos líquidos para consumo"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarCategoriaAPI(
                id=1,
                datos=datos,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE ACTUALIZAR LA CATEGORÍA."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE ACTUALIZACIÓN DE CATEGORÍAS
    def test_documentacion_openapi_actualizacion_categorias(self):
        esquema = app.openapi()
        ruta = "/api/v1/categorias/{id}"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("put", esquema["paths"][ruta])

        put_doc = esquema["paths"][ruta]["put"]
        self.assertIn("summary", put_doc)
        self.assertIn("description", put_doc)
        for codigo in ["200", "400", "404", "409", "500"]:
            self.assertIn(codigo, put_doc["responses"])


if __name__ == "__main__":
    unittest.main()
