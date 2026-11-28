import copy
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from pydantic import ValidationError

from main import app
from microservicios.clientes.api.clienteApi import (
    ActualizarClienteAPI,
    BuscarClientesAPI,
    ConsultarClientesAPI,
    ObtenerClientePorIdAPI,
    RegistrarClienteAPI
)
from microservicios.clientes.api.dtos import (
    ClienteActualizar,
    ClienteRegistro
)
from microservicios.clientes.repositorio import clienteRepositorio


# PRUEBAS UNITARIAS PARA EL REGISTRO DE CLIENTES
class TestRegistroClientes(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        clienteRepositorio.clientes.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: REGISTRO EXITOSO DE UN CLIENTE Y CONSULTA POSTERIOR
    def test_registro_exitoso_cliente(self):
        datos = ClienteRegistro(
            identificacion="1234567890",
            nombre="Juan Pérez",
            telefono="3001234567",
            correo="juan.perez@example.com"
        )

        respuesta = RegistrarClienteAPI(datos, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CLIENTE REGISTRADO EXITOSAMENTE.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["identificacion"], "1234567890")
        self.assertEqual(respuesta["data"]["nombre"], "Juan Pérez")
        self.assertEqual(respuesta["data"]["telefono"], "3001234567")
        self.assertEqual(respuesta["data"]["correo"], "juan.perez@example.com")

        # VERIFICAR QUE EL CLIENTE QUEDA DISPONIBLE PARA CONSULTA
        listado = ConsultarClientesAPI(self.superadministrador)
        self.assertTrue(listado["success"])
        self.assertEqual(len(listado["data"]), 1)

        detalle = ObtenerClientePorIdAPI(1, self.superadministrador)
        self.assertTrue(detalle["success"])
        self.assertEqual(detalle["data"]["identificacion"], "1234567890")

    # CASO 2: REGISTRO CON CAMPOS OBLIGATORIOS VACÍOS O FALTANTES
    def test_registro_campos_obligatorios_vacios_o_faltantes(self):
        with self.assertRaises(ValidationError) as contexto:
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567"
            )

        campos = [error["loc"][0] for error in contexto.exception.errors()]
        self.assertIn("correo", campos)

        with self.assertRaises(ValidationError):
            ClienteRegistro(
                identificacion="   ",
                nombre="   ",
                telefono="   ",
                correo="   "
            )

        self.assertEqual(len(clienteRepositorio.clientes), 0)

    # CASO 3: REGISTRO DE UN CLIENTE CON IDENTIFICACIÓN DUPLICADA
    def test_registro_cliente_duplicado(self):
        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="juan.perez@example.com"
            ),
            self.superadministrador
        )

        with self.assertRaises(HTTPException) as contexto:
            RegistrarClienteAPI(
                ClienteRegistro(
                    identificacion="1234567890",
                    nombre="Maria Gomez",
                    telefono="3119876543",
                    correo="maria@example.com"
                ),
                self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 409)
        self.assertEqual(
            contexto.exception.detail,
            "EL CLIENTE YA SE ENCUENTRA REGISTRADO."
        )
        self.assertEqual(len(clienteRepositorio.clientes), 1)

    # CASO 4: DATOS CON FORMATO INVÁLIDO
    def test_registro_formatos_invalidos(self):
        # IDENTIFICACIÓN NO NUMÉRICA
        with self.assertRaises(ValidationError):
            ClienteRegistro(
                identificacion="12345ABC",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="juan.perez@example.com"
            )

        # NOMBRE CON NÚMEROS
        with self.assertRaises(ValidationError):
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan 123",
                telefono="3001234567",
                correo="juan.perez@example.com"
            )

        # TELÉFONO NO NUMÉRICO
        with self.assertRaises(ValidationError):
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="300-ABC",
                correo="juan.perez@example.com"
            )

        # CORREO ELECTRÓNICO INVÁLIDO
        with self.assertRaises(ValidationError):
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="correo-invalido"
            )

        self.assertEqual(len(clienteRepositorio.clientes), 0)

    # CASO 5: ERROR AL GUARDAR EL CLIENTE
    @patch(
        "microservicios.clientes.repositorio.clienteRepositorio.RegistrarClienteRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_cliente(self, mock_guardar):
        datos = ClienteRegistro(
            identificacion="1234567890",
            nombre="Juan Pérez",
            telefono="3001234567",
            correo="juan.perez@example.com"
        )

        with self.assertRaises(HTTPException) as contexto:
            RegistrarClienteAPI(datos, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE COMPLETAR EL REGISTRO DEL CLIENTE."
        )
        self.assertEqual(len(clienteRepositorio.clientes), 0)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE REGISTRO DE CLIENTES
    def test_documentacion_openapi_registro_clientes(self):
        esquema = app.openapi()
        ruta = "/api/v1/clientes/"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

        post_doc = esquema["paths"][ruta]["post"]
        self.assertIn("summary", post_doc)
        self.assertIn("description", post_doc)
        for codigo in ["201", "400", "409", "500"]:
            self.assertIn(codigo, post_doc["responses"])


# PRUEBAS UNITARIAS PARA CONSULTAR Y LISTAR CLIENTES
class TestConsultaClientes(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        clienteRepositorio.clientes.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: CONSULTAR LISTADO DE CLIENTES REGISTRADOS
    def test_consulta_listado_clientes(self):
        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="juan.perez@example.com"
            ),
            self.superadministrador
        )
        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="9876543210",
                nombre="María López",
                telefono="3109876543",
                correo="maria.lopez@example.com"
            ),
            self.superadministrador
        )

        respuesta = ConsultarClientesAPI(self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CONSULTA DE CLIENTES EXITOSA.")
        self.assertEqual(len(respuesta["data"]), 2)
        self.assertEqual(respuesta["data"][0]["nombre"], "Juan Pérez")
        self.assertEqual(respuesta["data"][1]["nombre"], "María López")

    # CASO 2: CONSULTAR DETALLE DE UN CLIENTE SIN MODIFICAR LOS DATOS
    def test_consulta_detalle_cliente_sin_modificar(self):
        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="juan.perez@example.com"
            ),
            self.superadministrador
        )

        estado_antes = copy.deepcopy(clienteRepositorio.clientes)
        respuesta = ObtenerClientePorIdAPI(1, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CONSULTA DEL CLIENTE EXITOSA.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["identificacion"], "1234567890")
        self.assertEqual(respuesta["data"]["nombre"], "Juan Pérez")
        self.assertEqual(respuesta["data"]["telefono"], "3001234567")
        self.assertEqual(respuesta["data"]["correo"], "juan.perez@example.com")
        self.assertEqual(estado_antes, clienteRepositorio.clientes)

    # CASO 3: CONSULTAR CUANDO NO EXISTEN CLIENTES REGISTRADOS
    def test_consulta_sin_clientes_registrados(self):
        respuesta = ConsultarClientesAPI(self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "NO HAY CLIENTES REGISTRADOS.")
        self.assertEqual(respuesta["data"], [])

    # CASO 4: CONSULTAR UN CLIENTE INEXISTENTE
    def test_consulta_cliente_inexistente(self):
        with self.assertRaises(HTTPException) as contexto:
            ObtenerClientePorIdAPI(999, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "NO SE ENCONTRÓ EL CLIENTE SOLICITADO."
        )

    # CASO 5: ERROR DURANTE LA CONSULTA DE CLIENTES
    @patch(
        "microservicios.clientes.repositorio.clienteRepositorio.ConsultarClientesRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_listado_clientes(self, mock_consulta):
        with self.assertRaises(HTTPException) as contexto:
            ConsultarClientesAPI(self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR LOS CLIENTES."
        )

    @patch(
        "microservicios.clientes.repositorio.clienteRepositorio.ObtenerClientePorIdRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_detalle_cliente(self, mock_detalle):
        with self.assertRaises(HTTPException) as contexto:
            ObtenerClientePorIdAPI(1, self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR EL CLIENTE."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DE LOS ENDPOINTS DE CONSULTA DE CLIENTES
    def test_documentacion_openapi_consulta_clientes(self):
        esquema = app.openapi()

        ruta_lista = "/api/v1/clientes/"
        self.assertIn(ruta_lista, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta_lista])
        get_lista = esquema["paths"][ruta_lista]["get"]
        self.assertIn("summary", get_lista)
        self.assertIn("description", get_lista)
        self.assertIn("200", get_lista["responses"])
        self.assertIn("500", get_lista["responses"])

        ruta_detalle = "/api/v1/clientes/{id}"
        self.assertIn(ruta_detalle, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta_detalle])
        get_detalle = esquema["paths"][ruta_detalle]["get"]
        self.assertIn("summary", get_detalle)
        self.assertIn("description", get_detalle)
        for codigo in ["200", "404", "500"]:
            self.assertIn(codigo, get_detalle["responses"])


# PRUEBAS UNITARIAS PARA BUSCAR CLIENTES POR CRITERIOS
class TestBusquedaClientes(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        clienteRepositorio.clientes.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="juan.perez@example.com"
            ),
            self.superadministrador
        )
        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="9876543210",
                nombre="María López",
                telefono="3109876543",
                correo="maria.lopez@example.com"
            ),
            self.superadministrador
        )

    # CASO 1: BUSCAR CLIENTES POR NOMBRE
    def test_busqueda_por_nombre(self):
        respuesta = BuscarClientesAPI(
            identificacion=None,
            nombre="Juan",
            telefono=None,
            correo=None,
            superadministrador=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "BÚSQUEDA DE CLIENTES EXITOSA.")
        self.assertEqual(len(respuesta["data"]), 1)
        self.assertEqual(respuesta["data"][0]["nombre"], "Juan Pérez")

    # CASO 2: BUSCAR UN CLIENTE POR IDENTIFICACIÓN
    def test_busqueda_por_identificacion(self):
        respuesta = BuscarClientesAPI(
            identificacion="9876543210",
            nombre=None,
            telefono=None,
            correo=None,
            superadministrador=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(len(respuesta["data"]), 1)
        self.assertEqual(respuesta["data"][0]["nombre"], "María López")

    # CASO 3: BUSCAR CLIENTES POR TELÉFONO O CORREO SIN MODIFICAR DATOS
    def test_busqueda_por_telefono_y_correo_sin_modificar(self):
        estado_antes = copy.deepcopy(clienteRepositorio.clientes)

        por_telefono = BuscarClientesAPI(
            identificacion=None,
            nombre=None,
            telefono="3001234567",
            correo=None,
            superadministrador=self.superadministrador
        )
        self.assertEqual(len(por_telefono["data"]), 1)
        self.assertEqual(por_telefono["data"][0]["identificacion"], "1234567890")

        por_correo = BuscarClientesAPI(
            identificacion=None,
            nombre=None,
            telefono=None,
            correo="maria.lopez@example.com",
            superadministrador=self.superadministrador
        )
        self.assertEqual(len(por_correo["data"]), 1)
        self.assertEqual(por_correo["data"][0]["identificacion"], "9876543210")
        self.assertEqual(estado_antes, clienteRepositorio.clientes)

    # CASO 4: BÚSQUEDA SIN RESULTADOS
    def test_busqueda_sin_resultados(self):
        respuesta = BuscarClientesAPI(
            identificacion=None,
            nombre="Inexistente",
            telefono=None,
            correo=None,
            superadministrador=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "NO SE ENCONTRARON CLIENTES CON LOS CRITERIOS INGRESADOS."
        )
        self.assertEqual(respuesta["data"], [])

    # CASO 5: CRITERIOS DE BÚSQUEDA VACÍOS O INVÁLIDOS
    def test_busqueda_criterios_invalidos(self):
        with self.assertRaises(HTTPException) as sin_criterio:
            BuscarClientesAPI(
                identificacion="   ",
                nombre=None,
                telefono=None,
                correo=None,
                superadministrador=self.superadministrador
            )
        self.assertEqual(sin_criterio.exception.status_code, 400)

        with self.assertRaises(HTTPException) as id_invalido:
            BuscarClientesAPI(
                identificacion="12345ABC",
                nombre=None,
                telefono=None,
                correo=None,
                superadministrador=self.superadministrador
            )
        self.assertEqual(id_invalido.exception.status_code, 400)

        with self.assertRaises(HTTPException) as nombre_string:
            BuscarClientesAPI(
                identificacion=None,
                nombre="string",
                telefono=None,
                correo=None,
                superadministrador=self.superadministrador
            )
        self.assertEqual(nombre_string.exception.status_code, 400)

        with self.assertRaises(HTTPException) as nombre_numeros:
            BuscarClientesAPI(
                identificacion=None,
                nombre="Juan 123",
                telefono=None,
                correo=None,
                superadministrador=self.superadministrador
            )
        self.assertEqual(nombre_numeros.exception.status_code, 400)

        with self.assertRaises(HTTPException) as tel_invalido:
            BuscarClientesAPI(
                identificacion=None,
                nombre=None,
                telefono="300ABC",
                correo=None,
                superadministrador=self.superadministrador
            )
        self.assertEqual(tel_invalido.exception.status_code, 400)

    # CASO 6: ERROR DURANTE LA BÚSQUEDA DE CLIENTES
    @patch(
        "microservicios.clientes.repositorio.clienteRepositorio.BuscarClientesRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_busqueda_clientes(self, mock_buscar):
        with self.assertRaises(HTTPException) as contexto:
            BuscarClientesAPI(
                identificacion=None,
                nombre="Juan",
                telefono=None,
                correo=None,
                superadministrador=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE COMPLETAR LA BÚSQUEDA DE CLIENTES."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE BÚSQUEDA DE CLIENTES
    def test_documentacion_openapi_busqueda_clientes(self):
        esquema = app.openapi()
        ruta = "/api/v1/clientes/buscar"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta])

        get_doc = esquema["paths"][ruta]["get"]
        self.assertIn("summary", get_doc)
        self.assertIn("description", get_doc)
        for codigo in ["200", "400", "500"]:
            self.assertIn(codigo, get_doc["responses"])


# PRUEBAS UNITARIAS PARA ACTUALIZAR INFORMACIÓN DE CLIENTES
class TestActualizacionClientes(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        clienteRepositorio.clientes.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3001234567",
                correo="juan.perez@example.com"
            ),
            self.superadministrador
        )
        RegistrarClienteAPI(
            ClienteRegistro(
                identificacion="9876543210",
                nombre="María López",
                telefono="3109876543",
                correo="maria.lopez@example.com"
            ),
            self.superadministrador
        )

    # CASO 1: ACTUALIZACIÓN EXITOSA DE UN CLIENTE SIN CREAR NUEVO REGISTRO
    def test_actualizacion_exitosa_cliente(self):
        datos = ClienteActualizar(
            identificacion="1234567890",
            nombre="Juan Pérez Gómez",
            telefono="3007654321",
            correo="juan.gomez@example.com"
        )

        respuesta = ActualizarClienteAPI(
            id=1,
            datos=datos,
            superadministrador=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "CLIENTE ACTUALIZADO EXITOSAMENTE.")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Juan Pérez Gómez")
        self.assertEqual(respuesta["data"]["telefono"], "3007654321")
        self.assertEqual(respuesta["data"]["correo"], "juan.gomez@example.com")
        self.assertEqual(len(clienteRepositorio.clientes), 2)

        consulta = ObtenerClientePorIdAPI(1, self.superadministrador)
        self.assertEqual(consulta["data"]["nombre"], "Juan Pérez Gómez")

    # CASO 2: ACTUALIZACIÓN CON CAMPOS OBLIGATORIOS VACÍOS O FALTANTES
    def test_actualizacion_campos_obligatorios_vacios(self):
        with self.assertRaises(ValidationError):
            ClienteActualizar(
                identificacion="string",
                nombre="string",
                telefono="string",
                correo="string"
            )

        with self.assertRaises(ValidationError):
            ClienteRegistro(
                identificacion="1234567890",
                nombre="string",
                telefono="3001234567",
                correo="juan@example.com"
            )

        with self.assertRaises(ValidationError):
            ClienteActualizar(
                identificacion="   ",
                nombre="   ",
                telefono="   ",
                correo="   "
            )

        self.assertEqual(
            clienteRepositorio.ObtenerClientePorIdRepositorio(1)["nombre"],
            "Juan Pérez"
        )

    # CASO 3: ACTUALIZACIÓN DE UN CLIENTE INEXISTENTE
    def test_actualizacion_cliente_inexistente(self):
        datos = ClienteActualizar(
            identificacion="5555555555",
            nombre="Cliente Inexistente",
            telefono="3001112233",
            correo="inexistente@example.com"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarClienteAPI(
                id=999,
                datos=datos,
                superadministrador=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "NO SE ENCONTRÓ EL CLIENTE SOLICITADO."
        )

    # CASO 4: ACTUALIZACIÓN CON DATOS DE FORMATO INVÁLIDO
    def test_actualizacion_formatos_invalidos(self):
        with self.assertRaises(ValidationError):
            ClienteActualizar(
                identificacion="12345ABC",
                nombre="Juan Pérez",
                telefono="3007654321",
                correo="juan.gomez@example.com"
            )

        with self.assertRaises(ValidationError):
            ClienteActualizar(
                identificacion="1234567890",
                nombre="Juan 123",
                telefono="3007654321",
                correo="juan.gomez@example.com"
            )

        with self.assertRaises(ValidationError):
            ClienteActualizar(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="300ABC",
                correo="juan.gomez@example.com"
            )

        with self.assertRaises(ValidationError):
            ClienteActualizar(
                identificacion="1234567890",
                nombre="Juan Pérez",
                telefono="3007654321",
                correo="correo-invalido"
            )

        self.assertEqual(
            clienteRepositorio.ObtenerClientePorIdRepositorio(1)["correo"],
            "juan.perez@example.com"
        )

    # CASO 5: CONFLICTO POR IDENTIFICACIÓN DUPLICADA DE OTRO CLIENTE
    def test_actualizacion_identificacion_duplicada(self):
        datos = ClienteActualizar(
            identificacion="9876543210",
            nombre="Juan Pérez",
            telefono="3001234567",
            correo="juan.perez@example.com"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarClienteAPI(
                id=1,
                datos=datos,
                superadministrador=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 409)
        self.assertEqual(
            contexto.exception.detail,
            "LA IDENTIFICACIÓN YA SE ENCUENTRA REGISTRADA."
        )
        self.assertEqual(
            clienteRepositorio.ObtenerClientePorIdRepositorio(1)["identificacion"],
            "1234567890"
        )

    # CASO 6: ERROR AL GUARDAR LOS CAMBIOS DEL CLIENTE
    @patch(
        "microservicios.clientes.repositorio.clienteRepositorio.ActualizarClienteRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_actualizar_cliente(self, mock_actualizar):
        datos = ClienteActualizar(
            identificacion="1234567890",
            nombre="Juan Pérez Gómez",
            telefono="3007654321",
            correo="juan.gomez@example.com"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarClienteAPI(
                id=1,
                datos=datos,
                superadministrador=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE COMPLETAR LA ACTUALIZACIÓN DEL CLIENTE."
        )

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE ACTUALIZACIÓN DE CLIENTES
    def test_documentacion_openapi_actualizacion_clientes(self):
        esquema = app.openapi()
        ruta = "/api/v1/clientes/{id}"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("put", esquema["paths"][ruta])

        put_doc = esquema["paths"][ruta]["put"]
        self.assertIn("summary", put_doc)
        self.assertIn("description", put_doc)
        for codigo in ["200", "400", "404", "409", "500"]:
            self.assertIn(codigo, put_doc["responses"])


if __name__ == "__main__":
    unittest.main()
