import copy
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

from main import app
from microservicios.proveedores.api.dtos import (
    ProveedorActualizar,
    ProveedorRegistro
)
from microservicios.proveedores.api.proveedorApi import (
    ActualizarProveedorAPI,
    BuscarProveedoresAPI,
    ConsultarProveedoresAPI,
    ObtenerProveedorPorIdAPI,
    RegistrarProveedorAPI
)
from microservicios.proveedores.repositorio import proveedorRepositorio


# PRUEBAS UNITARIAS PARA EL REGISTRO DE PROVEEDORES
class TestRegistroProveedores(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        proveedorRepositorio.proveedores.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: REGISTRO EXITOSO DE UN PROVEEDOR Y CONSULTA POSTERIOR
    def test_registro_exitoso_proveedor(self):
        datos = ProveedorRegistro(
            identificacion="900123456",
            nombre="Distribuidora ABC S.A.S.",
            telefono="3001234567",
            correo="contacto@distribuidoraabc.com",
            direccion="Calle 10 # 20-30"
        )

        respuesta = RegistrarProveedorAPI(datos, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "PROVEEDOR REGISTRADO EXITOSAMENTE.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["identificacion"], "900123456")
        self.assertEqual(respuesta["data"]["nombre"], "Distribuidora ABC S.A.S.")
        self.assertEqual(respuesta["data"]["telefono"], "3001234567")
        self.assertEqual(respuesta["data"]["correo"], "contacto@distribuidoraabc.com")
        self.assertEqual(respuesta["data"]["direccion"], "Calle 10 # 20-30")

        # VERIFICAR QUE QUEDA DISPONIBLE PARA CONSULTA POSTERIOR
        listado = ConsultarProveedoresAPI(self.superadministrador)
        self.assertTrue(listado["success"])
        self.assertEqual(len(listado["data"]), 1)

        detalle = ObtenerProveedorPorIdAPI(1, self.superadministrador)
        self.assertTrue(detalle["success"])
        self.assertEqual(detalle["data"]["identificacion"], "900123456")

    # CASO 2: REGISTRO CON CAMPOS OBLIGATORIOS VACÍOS O FALTANTES
    def test_registro_campos_obligatorios_vacios_o_faltantes(self):
        with self.assertRaises(ValidationError) as contexto:
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com"
            )

        campos = [error["loc"][0] for error in contexto.exception.errors()]
        self.assertIn("direccion", campos)

        with self.assertRaises(ValidationError):
            ProveedorRegistro(
                identificacion="   ",
                nombre="   ",
                telefono="   ",
                correo="   ",
                direccion="   "
            )

        self.assertEqual(len(proveedorRepositorio.proveedores), 0)

    # CASO 3: REGISTRO DE UN PROVEEDOR CON IDENTIFICACIÓN DUPLICADA
    def test_registro_proveedor_duplicado(self):
        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            ),
            self.superadministrador
        )

        with self.assertRaises(HTTPException) as contexto:
            RegistrarProveedorAPI(
                ProveedorRegistro(
                    identificacion="900123456",
                    nombre="Otra Distribuidora",
                    telefono="3119876543",
                    correo="otro@distribuidora.com",
                    direccion="Carrera 5 # 12-40"
                ),
                self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 409)
        self.assertEqual(
            contexto.exception.detail,
            "EL PROVEEDOR YA SE ENCUENTRA REGISTRADO."
        )
        self.assertEqual(len(proveedorRepositorio.proveedores), 1)

    # CASO 4: DATOS CON FORMATO INVÁLIDO
    def test_registro_formatos_invalidos(self):
        # IDENTIFICACIÓN NO NUMÉRICA
        with self.assertRaises(ValidationError):
            ProveedorRegistro(
                identificacion="900123ABC",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            )

        # NOMBRE CON CARACTERES NO PERMITIDOS
        with self.assertRaises(ValidationError):
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora @#$%",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            )

        # TELÉFONO NO NUMÉRICO
        with self.assertRaises(ValidationError):
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="300-ABC",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            )

        # CORREO ELECTRÓNICO INVÁLIDO
        with self.assertRaises(ValidationError):
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="correo-invalido",
                direccion="Calle 10 # 20-30"
            )

        self.assertEqual(len(proveedorRepositorio.proveedores), 0)

    # CASO 5: ERROR AL GUARDAR EL PROVEEDOR
    @patch(
        "microservicios.proveedores.repositorio.proveedorRepositorio.RegistrarProveedorRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_proveedor(self, mock_guardar):
        datos = ProveedorRegistro(
            identificacion="900123456",
            nombre="Distribuidora ABC S.A.S.",
            telefono="3001234567",
            correo="contacto@distribuidoraabc.com",
            direccion="Calle 10 # 20-30"
        )

        with self.assertRaises(HTTPException) as contexto:
            RegistrarProveedorAPI(datos, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE REGISTRAR EL PROVEEDOR."
        )
        self.assertEqual(len(proveedorRepositorio.proveedores), 0)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE REGISTRO DE PROVEEDORES
    def test_documentacion_openapi_registro_proveedores(self):
        esquema = app.openapi()
        ruta = "/api/v1/proveedores/"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

        post_doc = esquema["paths"][ruta]["post"]
        self.assertIn("summary", post_doc)
        self.assertIn("description", post_doc)
        for codigo in ["201", "400", "409", "500"]:
            self.assertIn(codigo, post_doc["responses"])


# PRUEBAS UNITARIAS PARA CONSULTAR Y LISTAR PROVEEDORES
class TestConsultaProveedores(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        proveedorRepositorio.proveedores.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: CONSULTAR PROVEEDORES REGISTRADOS
    def test_consulta_proveedores_registrados(self):
        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            ),
            self.superadministrador
        )
        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="800987654",
                nombre="Comercializadora XYZ",
                telefono="3109876543",
                correo="ventas@xyz.com",
                direccion="Avenida 15 # 40-12"
            ),
            self.superadministrador
        )

        respuesta = ConsultarProveedoresAPI(self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CONSULTA DE PROVEEDORES EXITOSA.")
        self.assertEqual(len(respuesta["data"]), 2)
        self.assertEqual(respuesta["data"][0]["nombre"], "Distribuidora ABC S.A.S.")
        self.assertEqual(respuesta["data"][1]["nombre"], "Comercializadora XYZ")

    # CASO 2: CONSULTAR CUANDO NO EXISTEN PROVEEDORES REGISTRADOS
    def test_consulta_sin_proveedores_registrados(self):
        respuesta = ConsultarProveedoresAPI(self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "NO EXISTEN PROVEEDORES REGISTRADOS.")
        self.assertEqual(respuesta["data"], [])

    # CASO 3: CONSULTAR UN PROVEEDOR ESPECÍFICO SIN MODIFICAR LOS DATOS
    def test_consulta_proveedor_por_id_sin_modificar(self):
        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            ),
            self.superadministrador
        )

        estado_antes = copy.deepcopy(proveedorRepositorio.proveedores)
        respuesta = ObtenerProveedorPorIdAPI(1, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "PROVEEDOR CONSULTADO EXITOSAMENTE.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["identificacion"], "900123456")
        self.assertEqual(respuesta["data"]["nombre"], "Distribuidora ABC S.A.S.")
        self.assertEqual(estado_antes, proveedorRepositorio.proveedores)

    # CASO 4: CONSULTAR UN PROVEEDOR INEXISTENTE
    def test_consulta_proveedor_inexistente(self):
        with self.assertRaises(HTTPException) as contexto:
            ObtenerProveedorPorIdAPI(999, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO."
        )

    # CASO 5: ERROR DURANTE LA CONSULTA DE PROVEEDORES
    @patch(
        "microservicios.proveedores.repositorio.proveedorRepositorio.ConsultarProveedoresRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_listado_proveedores(self, mock_consulta):
        with self.assertRaises(HTTPException) as contexto:
            ConsultarProveedoresAPI(self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR LOS PROVEEDORES."
        )

    @patch(
        "microservicios.proveedores.repositorio.proveedorRepositorio.ObtenerProveedorPorIdRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_detalle_proveedor(self, mock_detalle):
        with self.assertRaises(HTTPException) as contexto:
            ObtenerProveedorPorIdAPI(1, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR EL PROVEEDOR."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DE LOS ENDPOINTS DE CONSULTA DE PROVEEDORES
    def test_documentacion_openapi_consulta_proveedores(self):
        esquema = app.openapi()

        ruta_lista = "/api/v1/proveedores/"
        self.assertIn(ruta_lista, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta_lista])
        get_lista = esquema["paths"][ruta_lista]["get"]
        self.assertIn("summary", get_lista)
        self.assertIn("description", get_lista)
        self.assertIn("200", get_lista["responses"])
        self.assertIn("500", get_lista["responses"])

        ruta_detalle = "/api/v1/proveedores/{id}"
        self.assertIn(ruta_detalle, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta_detalle])
        get_detalle = esquema["paths"][ruta_detalle]["get"]
        self.assertIn("summary", get_detalle)
        self.assertIn("description", get_detalle)
        for codigo in ["200", "404", "500"]:
            self.assertIn(codigo, get_detalle["responses"])


# PRUEBAS UNITARIAS PARA BUSCAR PROVEEDORES POR CRITERIOS
class TestBusquedaProveedores(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        proveedorRepositorio.proveedores.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            ),
            self.superadministrador
        )
        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="800987654",
                nombre="Comercializadora XYZ",
                telefono="3109876543",
                correo="ventas@xyz.com",
                direccion="Avenida 15 # 40-12"
            ),
            self.superadministrador
        )

    # CASO 1: BUSCAR PROVEEDOR POR NOMBRE
    def test_busqueda_por_nombre(self):
        respuesta = BuscarProveedoresAPI(
            nombre="Distribuidora",
            identificacion=None,
            telefono=None,
            correo=None,
            usuario_autenticado=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "BÚSQUEDA DE PROVEEDORES EXITOSA.")
        self.assertEqual(len(respuesta["data"]), 1)
        self.assertEqual(respuesta["data"][0]["nombre"], "Distribuidora ABC S.A.S.")

    # CASO 2: BUSCAR PROVEEDOR POR IDENTIFICACIÓN
    def test_busqueda_por_identificacion(self):
        respuesta = BuscarProveedoresAPI(
            nombre=None,
            identificacion="800987654",
            telefono=None,
            correo=None,
            usuario_autenticado=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(len(respuesta["data"]), 1)
        self.assertEqual(respuesta["data"][0]["nombre"], "Comercializadora XYZ")

    # CASO 3: BUSCAR PROVEEDOR POR TELÉFONO O CORREO SIN MODIFICAR DATOS
    def test_busqueda_por_telefono_y_correo_sin_modificar(self):
        estado_antes = copy.deepcopy(proveedorRepositorio.proveedores)

        por_telefono = BuscarProveedoresAPI(
            nombre=None,
            identificacion=None,
            telefono="3001234567",
            correo=None,
            usuario_autenticado=self.superadministrador
        )
        self.assertEqual(len(por_telefono["data"]), 1)
        self.assertEqual(por_telefono["data"][0]["identificacion"], "900123456")

        por_correo = BuscarProveedoresAPI(
            nombre=None,
            identificacion=None,
            telefono=None,
            correo="ventas@xyz.com",
            usuario_autenticado=self.superadministrador
        )
        self.assertEqual(len(por_correo["data"]), 1)
        self.assertEqual(por_correo["data"][0]["identificacion"], "800987654")
        self.assertEqual(estado_antes, proveedorRepositorio.proveedores)

    # CASO 4: BÚSQUEDA SIN RESULTADOS
    def test_busqueda_sin_resultados(self):
        respuesta = BuscarProveedoresAPI(
            nombre="Inexistente",
            identificacion=None,
            telefono=None,
            correo=None,
            usuario_autenticado=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "NO SE ENCONTRARON PROVEEDORES CON LOS CRITERIOS INGRESADOS."
        )
        self.assertEqual(respuesta["data"], [])

    # CASO 5: CRITERIOS DE BÚSQUEDA VACÍOS O INVÁLIDOS
    def test_busqueda_criterios_vacios_e_invalidos(self):
        with self.assertRaises(HTTPException) as sin_criterio:
            BuscarProveedoresAPI(
                nombre="   ",
                identificacion=None,
                telefono=None,
                correo=None,
                usuario_autenticado=self.superadministrador
            )
        self.assertEqual(sin_criterio.exception.status_code, 400)

        with self.assertRaises(HTTPException) as id_invalido:
            BuscarProveedoresAPI(
                nombre=None,
                identificacion="900ABC",
                telefono=None,
                correo=None,
                usuario_autenticado=self.superadministrador
            )
        self.assertEqual(id_invalido.exception.status_code, 400)

        with self.assertRaises(HTTPException) as nombre_string:
            BuscarProveedoresAPI(
                nombre="string",
                identificacion=None,
                telefono=None,
                correo=None,
                usuario_autenticado=self.superadministrador
            )
        self.assertEqual(nombre_string.exception.status_code, 400)

        with self.assertRaises(HTTPException) as tel_invalido:
            BuscarProveedoresAPI(
                nombre=None,
                identificacion=None,
                telefono="300ABC",
                correo=None,
                usuario_autenticado=self.superadministrador
            )
        self.assertEqual(tel_invalido.exception.status_code, 400)

    # CASO 6: ERROR DURANTE LA BÚSQUEDA DE PROVEEDORES
    @patch(
        "microservicios.proveedores.repositorio.proveedorRepositorio.BuscarProveedoresRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_busqueda_proveedores(self, mock_buscar):
        with self.assertRaises(HTTPException) as contexto:
            BuscarProveedoresAPI(
                nombre="Distribuidora",
                identificacion=None,
                telefono=None,
                correo=None,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE REALIZAR LA BÚSQUEDA DE PROVEEDORES."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE BÚSQUEDA DE PROVEEDORES
    def test_documentacion_openapi_busqueda_proveedores(self):
        esquema = app.openapi()
        ruta = "/api/v1/proveedores/buscar"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta])

        get_doc = esquema["paths"][ruta]["get"]
        self.assertIn("summary", get_doc)
        self.assertIn("description", get_doc)
        for codigo in ["200", "400", "500"]:
            self.assertIn(codigo, get_doc["responses"])


# PRUEBAS UNITARIAS PARA ACTUALIZAR INFORMACIÓN DE PROVEEDORES
class TestActualizacionProveedores(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        proveedorRepositorio.proveedores.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="900123456",
                nombre="Distribuidora ABC S.A.S.",
                telefono="3001234567",
                correo="contacto@distribuidoraabc.com",
                direccion="Calle 10 # 20-30"
            ),
            self.superadministrador
        )
        RegistrarProveedorAPI(
            ProveedorRegistro(
                identificacion="800987654",
                nombre="Comercializadora XYZ",
                telefono="3109876543",
                correo="ventas@xyz.com",
                direccion="Avenida 15 # 40-12"
            ),
            self.superadministrador
        )

    # CASO 1: ACTUALIZACIÓN EXITOSA DE UN PROVEEDOR
    def test_actualizacion_exitosa_proveedor(self):
        datos = ProveedorActualizar(
            identificacion="900123456",
            nombre="Proveedor actualizado",
            telefono="3009876543",
            correo="contacto@proveedor.com",
            direccion="Calle 10 # 20-30"
        )

        respuesta = ActualizarProveedorAPI(
            id=1,
            datos=datos,
            usuario_autenticado=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "PROVEEDOR ACTUALIZADO EXITOSAMENTE.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Proveedor actualizado")
        self.assertEqual(respuesta["data"]["telefono"], "3009876543")
        self.assertEqual(respuesta["data"]["correo"], "contacto@proveedor.com")
        self.assertEqual(len(proveedorRepositorio.proveedores), 2)

        consulta = ObtenerProveedorPorIdAPI(1, self.superadministrador)
        self.assertEqual(consulta["data"]["nombre"], "Proveedor actualizado")

    # CASO 2: ACTUALIZAR DATOS CONSERVANDO CAMPOS NO MODIFICADOS Y OTROS PROVEEDORES
    def test_actualizacion_conserva_campos_y_otros_proveedores(self):
        proveedor_2_antes = copy.deepcopy(
            proveedorRepositorio.ObtenerProveedorPorIdRepositorio(2)
        )

        datos = ProveedorActualizar(
            identificacion="900123456",
            nombre="Distribuidora ABC S.A.S.",
            telefono="3007778899",
            correo="contacto@distribuidoraabc.com",
            direccion="Calle 50 # 10-20"
        )

        respuesta = ActualizarProveedorAPI(
            id=1,
            datos=datos,
            usuario_autenticado=self.superadministrador
        )

        self.assertEqual(respuesta["data"]["nombre"], "Distribuidora ABC S.A.S.")
        self.assertEqual(respuesta["data"]["telefono"], "3007778899")
        self.assertEqual(respuesta["data"]["direccion"], "Calle 50 # 10-20")
        self.assertEqual(
            proveedor_2_antes,
            proveedorRepositorio.ObtenerProveedorPorIdRepositorio(2)
        )

    # CASO 3: INTENTAR ACTUALIZAR UN PROVEEDOR INEXISTENTE
    def test_actualizacion_proveedor_inexistente(self):
        datos = ProveedorActualizar(
            identificacion="555555555",
            nombre="Proveedor Inexistente",
            telefono="3001112233",
            correo="inexistente@proveedor.com",
            direccion="Calle 1 # 2-3"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarProveedorAPI(
                id=999,
                datos=datos,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "NO SE ENCONTRÓ EL PROVEEDOR SOLICITADO."
        )

    # CASO 4: CAMPOS OBLIGATORIOS VACÍOS O CON FORMATO INVÁLIDO
    def test_actualizacion_campos_vacios_o_invalidos(self):
        with self.assertRaises(ValidationError):
            ProveedorActualizar(
                identificacion="string",
                nombre="string",
                telefono="string",
                correo="string",
                direccion="string"
            )

        with self.assertRaises(ValidationError):
            ProveedorRegistro(
                identificacion="900123456",
                nombre="string",
                telefono="3001234567",
                correo="contacto@proveedor.com",
                direccion="Calle 10 # 20-30"
            )

        with self.assertRaises(ValidationError):
            ProveedorActualizar(
                identificacion="   ",
                nombre="   ",
                telefono="   ",
                correo="   ",
                direccion="   "
            )

        with self.assertRaises(ValidationError):
            ProveedorActualizar(
                identificacion="900ABC",
                nombre="Proveedor @#$",
                telefono="300ABC",
                correo="correo-invalido",
                direccion="Calle 10 # 20-30"
            )

        self.assertEqual(
            proveedorRepositorio.ObtenerProveedorPorIdRepositorio(1)["nombre"],
            "Distribuidora ABC S.A.S."
        )

    # CASO 5: CONFLICTO POR IDENTIFICACIÓN DUPLICADA DE OTRO PROVEEDOR
    def test_actualizacion_identificacion_duplicada(self):
        datos = ProveedorActualizar(
            identificacion="800987654",
            nombre="Distribuidora ABC S.A.S.",
            telefono="3001234567",
            correo="contacto@distribuidoraabc.com",
            direccion="Calle 10 # 20-30"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarProveedorAPI(
                id=1,
                datos=datos,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 409)
        self.assertEqual(
            contexto.exception.detail,
            "LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA."
        )
        self.assertEqual(
            proveedorRepositorio.ObtenerProveedorPorIdRepositorio(1)["identificacion"],
            "900123456"
        )

    # CASO 6: ERROR AL GUARDAR LOS CAMBIOS DEL PROVEEDOR
    @patch(
        "microservicios.proveedores.repositorio.proveedorRepositorio.ActualizarProveedorRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_actualizar_proveedor(self, mock_actualizar):
        datos = ProveedorActualizar(
            identificacion="900123456",
            nombre="Proveedor actualizado",
            telefono="3009876543",
            correo="contacto@proveedor.com",
            direccion="Calle 10 # 20-30"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarProveedorAPI(
                id=1,
                datos=datos,
                usuario_autenticado=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE ACTUALIZAR EL PROVEEDOR."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE ACTUALIZACIÓN DE PROVEEDORES
    def test_documentacion_openapi_actualizacion_proveedores(self):
        esquema = app.openapi()
        ruta = "/api/v1/proveedores/{id}"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("put", esquema["paths"][ruta])

        put_doc = esquema["paths"][ruta]["put"]
        self.assertIn("summary", put_doc)
        self.assertIn("description", put_doc)
        for codigo in ["200", "400", "404", "409", "500"]:
            self.assertIn(codigo, put_doc["responses"])


if __name__ == "__main__":
    unittest.main()
