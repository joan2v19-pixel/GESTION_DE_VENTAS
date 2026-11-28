import copy
import json
import unittest
from unittest.mock import patch

from fastapi import HTTPException, Response
from pydantic import ValidationError

from main import app
from microservicios.usuarios.api.dtos import (
    UsuarioActualizar,
    UsuarioLogin,
    UsuarioRegistro
)
from microservicios.usuarios.api.usuarioApi import (
    ActualizarUsuarioAPI,
    CerrarSesionAPI,
    ConsultarUsuariosAPI,
    IniciarSesionAPI,
    ObtenerSuperadministrador,
    ObtenerUsuarioAutenticado,
    RegistrarUsuarioAPI
)
from microservicios.usuarios.repositorio import usuarioRepositorio


# PRUEBAS UNITARIAS PARA EL REGISTRO DE USUARIOS
class TestRegistroUsuarios(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        usuarioRepositorio.usuarios.clear()
        usuarioRepositorio.sesiones.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: REGISTRO EXITOSO DE UN USUARIO Y CONSULTA POSTERIOR
    def test_registro_exitoso_usuario(self):
        datos = UsuarioRegistro(
            nombre="Joan Sierra",
            identificacion="1234567890",
            nombreUsuario="Joan",
            contrasena="ClaveSegura123*"
        )

        respuesta = RegistrarUsuarioAPI(datos, self.superadministrador)

        self.assertTrue(respuesta["success"])
        self.assertEqual(respuesta["message"], "Usuario registrado correctamente")
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Joan Sierra")
        self.assertEqual(respuesta["data"]["identificacion"], "1234567890")
        self.assertEqual(respuesta["data"]["nombreUsuario"], "Joan")
        # VERIFICAR QUE LA RESPUESTA NO INCLUYA LA CONTRASEÑA NI SU HASH
        self.assertNotIn("contrasena", respuesta["data"])

        # VERIFICAR QUE LA CONTRASEÑA SE ALMACENÓ HASHEADA Y NO EN TEXTO PLANO
        almacenado = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(1)
        self.assertIsNotNone(almacenado)
        self.assertNotEqual(almacenado["contrasena"], "ClaveSegura123*")
        self.assertFalse(almacenado["esSuperadministrador"])
        self.assertTrue(almacenado["estado"])

        # VERIFICAR QUE EL USUARIO PUEDE CONSULTARSE POSTERIORMENTE
        consulta = ConsultarUsuariosAPI(self.superadministrador)
        self.assertTrue(consulta["success"])
        self.assertEqual(len(consulta["data"]), 1)
        self.assertEqual(consulta["data"][0]["nombreUsuario"], "Joan")
        self.assertNotIn("contrasena", consulta["data"][0])

    # CASO 2: REGISTRO CON CAMPOS OBLIGATORIOS VACÍOS O FALTANTES
    def test_registro_campos_obligatorios_vacios_o_faltantes(self):
        with self.assertRaises(ValidationError) as contexto:
            UsuarioRegistro(
                nombre="Joan Sierra",
                identificacion="1234567890",
                nombreUsuario="Joan"
            )

        campos = [error["loc"][0] for error in contexto.exception.errors()]
        self.assertIn("contrasena", campos)

        with self.assertRaises(ValidationError):
            UsuarioRegistro(
                nombre="   ",
                identificacion="   ",
                nombreUsuario="   ",
                contrasena="   "
            )

        self.assertEqual(len(usuarioRepositorio.usuarios), 0)

    # CASO 3: REGISTRO DE USUARIO DUPLICADO POR IDENTIFICACIÓN O NOMBRE DE USUARIO
    def test_registro_usuario_duplicado(self):
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Joan Sierra",
                identificacion="1234567890",
                nombreUsuario="Joan",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

        # IDENTIFICACIÓN DUPLICADA
        resp_id = RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Carlos Perez",
                identificacion="1234567890",
                nombreUsuario="Carlos",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )
        cuerpo_id = json.loads(resp_id.body.decode("utf-8"))
        self.assertEqual(resp_id.status_code, 409)
        self.assertFalse(cuerpo_id["success"])
        self.assertIsNone(cuerpo_id["data"])
        self.assertEqual(cuerpo_id["message"], "La identificación ya está registrada")

        # NOMBRE DE USUARIO DUPLICADO (INSENSIBLE A MAYÚSCULAS)
        resp_user = RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Carlos Perez",
                identificacion="9876543210",
                nombreUsuario="joan",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )
        cuerpo_user = json.loads(resp_user.body.decode("utf-8"))
        self.assertEqual(resp_user.status_code, 409)
        self.assertFalse(cuerpo_user["success"])
        self.assertIsNone(cuerpo_user["data"])
        self.assertEqual(cuerpo_user["message"], "El nombre de usuario ya existe")

        self.assertEqual(len(usuarioRepositorio.usuarios), 1)

    # CASO 4: REGISTRO CON DATOS INVÁLIDOS
    def test_registro_datos_invalidos(self):
        # NOMBRE CON NÚMEROS
        with self.assertRaises(ValidationError):
            UsuarioRegistro(
                nombre="Joan 123",
                identificacion="1234567890",
                nombreUsuario="Joan",
                contrasena="ClaveSegura123*"
            )

        # IDENTIFICACIÓN NO NUMÉRICA
        with self.assertRaises(ValidationError):
            UsuarioRegistro(
                nombre="Joan Sierra",
                identificacion="12345ABC",
                nombreUsuario="Joan",
                contrasena="ClaveSegura123*"
            )

        # NOMBRE DE USUARIO CON CARACTERES INVÁLIDOS
        with self.assertRaises(ValidationError):
            UsuarioRegistro(
                nombre="Joan Sierra",
                identificacion="1234567890",
                nombreUsuario="Joan@2026!",
                contrasena="ClaveSegura123*"
            )

        # CONTRASEÑA DÉBIL (SIN CARÁCTER ESPECIAL, SIN MAYÚSCULA O SIN NÚMERO)
        for clave_invalida in ["clavesegura123*", "CLAVESEGURA123*", "ClaveSegura*", "ClaveSegura123"]:
            with self.assertRaises(ValidationError):
                UsuarioRegistro(
                    nombre="Joan Sierra",
                    identificacion="1234567890",
                    nombreUsuario="Joan",
                    contrasena=clave_invalida
                )

        self.assertEqual(len(usuarioRepositorio.usuarios), 0)

    # CASO 5: ERROR DE ALMACENAMIENTO AL REGISTRAR USUARIO
    @patch(
        "microservicios.usuarios.repositorio.usuarioRepositorio.RegistrarUsuarioRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_al_guardar_usuario(self, mock_guardar):
        datos = UsuarioRegistro(
            nombre="Joan Sierra",
            identificacion="1234567890",
            nombreUsuario="Joan",
            contrasena="ClaveSegura123*"
        )

        respuesta = RegistrarUsuarioAPI(datos, self.superadministrador)
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertIsNone(cuerpo["data"])
        self.assertEqual(cuerpo["message"], "No fue posible registrar el usuario")
        self.assertEqual(len(usuarioRepositorio.usuarios), 0)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE REGISTRO
    def test_documentacion_openapi_registro_usuarios(self):
        esquema = app.openapi()
        ruta = "/api/Usuarios/"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

        post_doc = esquema["paths"][ruta]["post"]
        self.assertIn("summary", post_doc)
        self.assertIn("description", post_doc)
        self.assertIn("201", post_doc["responses"])
        self.assertIn("400", post_doc["responses"])
        self.assertIn("409", post_doc["responses"])
        self.assertIn("500", post_doc["responses"])


# PRUEBAS UNITARIAS PARA CONSULTAR Y LISTAR USUARIOS
class TestConsultaUsuarios(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        usuarioRepositorio.usuarios.clear()
        usuarioRepositorio.sesiones.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

    # CASO 1: CONSULTAR USUARIOS REGISTRADOS Y ACTUALIZACIÓN AL AGREGAR NUEVOS
    def test_consulta_usuarios_registrados_y_actualizacion(self):
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Laura Gomez",
                identificacion="123456789",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Carlos Perez",
                identificacion="987654321",
                nombreUsuario="carlos.perez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

        resultado = ConsultarUsuariosAPI(self.superadministrador)
        self.assertTrue(resultado["success"])
        self.assertEqual(len(resultado["data"]), 2)
        self.assertEqual(resultado["data"][0]["nombre"], "Laura Gomez")
        self.assertEqual(resultado["data"][0]["identificacion"], "123456789")
        self.assertEqual(resultado["data"][0]["nombreUsuario"], "laura.gomez")
        self.assertEqual(resultado["data"][1]["nombreUsuario"], "carlos.perez")

        # VERIFICAR QUE AL REGISTRAR OTRO USUARIO, LA NUEVA CONSULTA LO REFLEJA
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Ana Ruiz",
                identificacion="112233445",
                nombreUsuario="ana.ruiz",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )
        actualizado = ConsultarUsuariosAPI(self.superadministrador)
        self.assertEqual(len(actualizado["data"]), 3)
        self.assertEqual(actualizado["data"][2]["nombreUsuario"], "ana.ruiz")

    # CASO 2: CONSULTAR CUANDO NO EXISTEN USUARIOS REGISTRADOS
    def test_consulta_listado_vacio(self):
        resultado = ConsultarUsuariosAPI(self.superadministrador)
        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["data"], [])

    # CASO 3: VERIFICAR QUE NO SE EXPONEN CONTRASEÑAS NI HASHES
    def test_consulta_no_expone_contrasenas(self):
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Laura Gomez",
                identificacion="123456789",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

        resultado = ConsultarUsuariosAPI(self.superadministrador)
        self.assertEqual(len(resultado["data"]), 1)
        self.assertNotIn("contrasena", resultado["data"][0])
        self.assertEqual(
            set(resultado["data"][0].keys()),
            {"id", "nombre", "identificacion", "nombreUsuario", "estado"}
        )

    # CASO 4: ERROR DURANTE LA CONSULTA DE USUARIOS
    @patch(
        "microservicios.usuarios.repositorio.usuarioRepositorio.ObtenerTodosUsuariosRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_consulta_usuarios(self, mock_consulta):
        with self.assertRaises(HTTPException) as contexto:
            ConsultarUsuariosAPI(self.superadministrador)

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE CONSULTAR LOS USUARIOS."
        )

    # CASO 5: ACCESO RESTRINGIDO AL SUPERADMINISTRADOR (401 SIN SESIÓN, 403 SIN PERMISOS)
    def test_acceso_restringido_consulta_usuarios(self):
        with self.assertRaises(HTTPException) as sin_sesion:
            ObtenerUsuarioAutenticado(sesion=None)
        self.assertEqual(sin_sesion.exception.status_code, 401)

        usuario_normal = {
            "id": 2,
            "nombreUsuario": "vendedor",
            "esSuperadministrador": False
        }
        with self.assertRaises(HTTPException) as sin_permisos:
            ObtenerSuperadministrador(usuario=usuario_normal)
        self.assertEqual(sin_permisos.exception.status_code, 403)

    # CASO 6: VERIFICAR QUE LA CONSULTA ES DE SOLO LECTURA Y NO MODIFICA LOS REGISTROS
    def test_consulta_no_modifica_registros(self):
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Laura Gomez",
                identificacion="123456789",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

        estado_antes = copy.deepcopy(usuarioRepositorio.usuarios)
        ConsultarUsuariosAPI(self.superadministrador)
        estado_despues = usuarioRepositorio.usuarios

        self.assertEqual(estado_antes, estado_despues)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE CONSULTA DE USUARIOS
    def test_documentacion_openapi_consulta_usuarios(self):
        esquema = app.openapi()
        ruta = "/api/Usuarios/"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("get", esquema["paths"][ruta])

        get_doc = esquema["paths"][ruta]["get"]
        self.assertIn("summary", get_doc)
        self.assertIn("description", get_doc)
        self.assertIn("200", get_doc["responses"])
        self.assertIn("401", get_doc["responses"])
        self.assertIn("403", get_doc["responses"])
        self.assertIn("500", get_doc["responses"])


# PRUEBAS UNITARIAS PARA ACTUALIZAR INFORMACIÓN DE USUARIOS
class TestActualizacionUsuarios(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        usuarioRepositorio.usuarios.clear()
        usuarioRepositorio.sesiones.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Laura Gomez",
                identificacion="123456789",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )
        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Carlos Perez",
                identificacion="987654321",
                nombreUsuario="carlos.perez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

    # CASO 1: ACTUALIZAR UN USUARIO CORRECTAMENTE SIN EXPONER CONTRASEÑA
    def test_actualizacion_exitosa_usuario(self):
        hash_original = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(1)["contrasena"]
        datos = UsuarioActualizar(
            nombre="Laura Maria Gomez",
            identificacion="123456789",
            nombreUsuario="laura.mgomez"
        )

        respuesta = ActualizarUsuarioAPI(
            id_usuario=1,
            datos=datos,
            superadministrador=self.superadministrador
        )

        self.assertTrue(respuesta["success"])
        self.assertEqual(
            respuesta["message"],
            "LA INFORMACIÓN DEL USUARIO SE ACTUALIZÓ CORRECTAMENTE."
        )
        self.assertEqual(respuesta["data"]["id"], 1)
        self.assertEqual(respuesta["data"]["nombre"], "Laura Maria Gomez")
        self.assertEqual(respuesta["data"]["nombreUsuario"], "laura.mgomez")
        self.assertNotIn("contrasena", respuesta["data"])

        almacenado = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(1)
        self.assertEqual(almacenado["nombre"], "Laura Maria Gomez")
        self.assertEqual(almacenado["contrasena"], hash_original)

    # CASO 2: INTENTAR ACTUALIZAR UN USUARIO INEXISTENTE
    def test_actualizacion_usuario_inexistente(self):
        datos = UsuarioActualizar(
            nombre="Usuario Fantasma",
            identificacion="555555555",
            nombreUsuario="fantasma"
        )

        with self.assertRaises(HTTPException) as contexto:
            ActualizarUsuarioAPI(
                id_usuario=999,
                datos=datos,
                superadministrador=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(
            contexto.exception.detail,
            "NO SE ENCONTRÓ EL USUARIO SOLICITADO."
        )

    # CASO 3: CAMPOS OBLIGATORIOS VACÍOS O CON FORMATO INVÁLIDO
    def test_actualizacion_campos_vacios_o_invalidos(self):
        with self.assertRaises(ValidationError):
            UsuarioActualizar(
                nombre="string",
                identificacion="string",
                nombreUsuario="string"
            )

        with self.assertRaises(ValidationError):
            UsuarioRegistro(
                nombre="string",
                identificacion="1234567890",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            )

        with self.assertRaises(ValidationError):
            UsuarioActualizar(
                nombre="   ",
                identificacion="123456789",
                nombreUsuario="laura.gomez"
            )

        with self.assertRaises(ValidationError):
            UsuarioActualizar(
                nombre="Laura 123",
                identificacion="ABCDE",
                nombreUsuario="laura@gomez"
            )

        self.assertEqual(
            usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(1)["nombre"],
            "Laura Gomez"
        )

    # CASO 4: DATOS DUPLICADOS DE OTRO USUARIO
    def test_actualizacion_datos_duplicados(self):
        # IDENTIFICACIÓN PERTENECIENTE AL USUARIO 2
        with self.assertRaises(HTTPException) as err_id:
            ActualizarUsuarioAPI(
                id_usuario=1,
                datos=UsuarioActualizar(
                    nombre="Laura Gomez",
                    identificacion="987654321",
                    nombreUsuario="laura.gomez"
                ),
                superadministrador=self.superadministrador
            )
        self.assertEqual(err_id.exception.status_code, 409)
        self.assertEqual(err_id.exception.detail, "La identificación ya está registrada")

        # NOMBRE DE USUARIO PERTENECIENTE AL USUARIO 2
        with self.assertRaises(HTTPException) as err_user:
            ActualizarUsuarioAPI(
                id_usuario=1,
                datos=UsuarioActualizar(
                    nombre="Laura Gomez",
                    identificacion="123456789",
                    nombreUsuario="CARLOS.PEREZ"
                ),
                superadministrador=self.superadministrador
            )
        self.assertEqual(err_user.exception.status_code, 409)
        self.assertEqual(err_user.exception.detail, "El nombre de usuario ya existe")

        # VERIFICAR QUE EL REGISTRO NO CAMBIÓ
        self.assertEqual(
            usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(1)["nombreUsuario"],
            "laura.gomez"
        )

    # CASO 5: ERROR AL GUARDAR LOS CAMBIOS
    @patch(
        "microservicios.usuarios.repositorio.usuarioRepositorio.ActualizarUsuarioRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_error_durante_actualizacion_usuario(self, mock_actualizar):
        with self.assertRaises(HTTPException) as contexto:
            ActualizarUsuarioAPI(
                id_usuario=1,
                datos=UsuarioActualizar(
                    nombre="Laura Nueva",
                    identificacion="123456789",
                    nombreUsuario="laura.gomez"
                ),
                superadministrador=self.superadministrador
            )

        self.assertEqual(contexto.exception.status_code, 500)
        self.assertEqual(
            contexto.exception.detail,
            "NO FUE POSIBLE ACTUALIZAR LA INFORMACIÓN DEL USUARIO."
        )

    # CASO 6: VERIFICAR QUE NO SE MODIFIQUEN OTROS USUARIOS
    def test_actualizacion_no_modifica_otros_usuarios(self):
        usuario_2_antes = copy.deepcopy(
            usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(2)
        )

        ActualizarUsuarioAPI(
            id_usuario=1,
            datos=UsuarioActualizar(
                nombre="Laura Actualizada",
                identificacion="111222333",
                nombreUsuario="laura.nueva"
            ),
            superadministrador=self.superadministrador
        )

        usuario_2_despues = usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(2)
        self.assertEqual(usuario_2_antes, usuario_2_despues)

    # CASO 7: ACCESO RESTRINGIDO AL SUPERADMINISTRADOR
    def test_acceso_restringido_actualizacion_usuario(self):
        with self.assertRaises(HTTPException) as sin_sesion:
            ObtenerUsuarioAutenticado(sesion=None)
        self.assertEqual(sin_sesion.exception.status_code, 401)

        with self.assertRaises(HTTPException) as sin_permisos:
            ObtenerSuperadministrador(
                usuario={"id": 2, "nombreUsuario": "carlos", "esSuperadministrador": False}
            )
        self.assertEqual(sin_permisos.exception.status_code, 403)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE ACTUALIZACIÓN
    def test_documentacion_openapi_actualizacion_usuario(self):
        esquema = app.openapi()
        ruta = "/api/Usuarios/{id_usuario}"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("put", esquema["paths"][ruta])

        put_doc = esquema["paths"][ruta]["put"]
        self.assertIn("summary", put_doc)
        self.assertIn("description", put_doc)
        for codigo in ["200", "401", "403", "404", "409", "500"]:
            self.assertIn(codigo, put_doc["responses"])


# PRUEBAS UNITARIAS PARA INICIAR SESIÓN EN EL SISTEMA
class TestLoginUsuarios(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        usuarioRepositorio.usuarios.clear()
        usuarioRepositorio.sesiones.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Laura Gomez",
                identificacion="123456789",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

    # CASO 1: INICIO DE SESIÓN EXITOSO SIN EXPONER CONTRASEÑA
    def test_login_exitoso(self):
        response = Response()
        datos = UsuarioLogin(
            nombreUsuario="laura.gomez",
            contrasena="ClaveSegura123*"
        )

        resultado = IniciarSesionAPI(datos=datos, response=response)

        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["message"], "INICIO DE SESIÓN EXITOSO.")
        self.assertEqual(resultado["data"]["id"], 1)
        self.assertEqual(resultado["data"]["nombre"], "Laura Gomez")
        self.assertEqual(resultado["data"]["nombreUsuario"], "laura.gomez")
        self.assertNotIn("contrasena", resultado["data"])
        self.assertEqual(len(usuarioRepositorio.sesiones), 1)
        self.assertIn("sesion=", response.headers.get("set-cookie", ""))

    # CASO 2: CREDENCIALES INCORRECTAS (USUARIO INEXISTENTE O CONTRASEÑA ERRÓNEA)
    def test_login_credenciales_incorrectas(self):
        err_pass = IniciarSesionAPI(
            datos=UsuarioLogin(
                nombreUsuario="laura.gomez",
                contrasena="ClaveIncorrecta1*"
            ),
            response=Response()
        )
        self.assertEqual(err_pass.status_code, 401)
        self.assertIn(b"Usuario o contrase", err_pass.body)

        err_user = IniciarSesionAPI(
            datos=UsuarioLogin(
                nombreUsuario="no.existe",
                contrasena="ClaveSegura123*"
            ),
            response=Response()
        )
        self.assertEqual(err_user.status_code, 401)
        self.assertIn(b"Usuario o contrase", err_user.body)
        self.assertEqual(len(usuarioRepositorio.sesiones), 0)

    # CASO 3: CAMPOS OBLIGATORIOS VACÍOS O FALTANTES
    def test_login_campos_vacios(self):
        with self.assertRaises(ValidationError):
            UsuarioLogin(nombreUsuario="laura.gomez")

        with self.assertRaises(ValidationError):
            UsuarioLogin(nombreUsuario="   ", contrasena="   ")

        self.assertEqual(len(usuarioRepositorio.sesiones), 0)

    # CASO 4: CUENTA INACTIVA IMPIDE EL ACCESO
    def test_login_cuenta_inactiva(self):
        usuarioRepositorio.ObtenerUsuarioPorIdRepositorio(1)["estado"] = False

        respuesta = IniciarSesionAPI(
            datos=UsuarioLogin(
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            response=Response()
        )

        self.assertEqual(respuesta.status_code, 403)
        self.assertIn(b"habilitada", respuesta.body)
        self.assertEqual(len(usuarioRepositorio.sesiones), 0)

    # CASO 5: ERROR DE CONEXIÓN O BASE DE DATOS DURANTE LA AUTENTICACIÓN
    @patch(
        "microservicios.usuarios.repositorio.usuarioRepositorio.ObtenerUsuarioPorNombreUsuarioRepositorio",
        side_effect=RuntimeError("Error simulado de base de datos")
    )
    def test_login_error_servidor(self, mock_consulta):
        respuesta = IniciarSesionAPI(
            datos=UsuarioLogin(
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            response=Response()
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertIn(b"No fue posible completar la autenticaci", respuesta.body)
        self.assertEqual(len(usuarioRepositorio.sesiones), 0)

    # CASO 6: INTENTO DE ACCESO A FUNCIONALIDAD PROTEGIDA SIN AUTENTICACIÓN
    def test_acceso_protegido_sin_autenticacion(self):
        with self.assertRaises(HTTPException) as sin_cookie:
            ObtenerUsuarioAutenticado(sesion=None)
        self.assertEqual(sin_cookie.exception.status_code, 401)

        with self.assertRaises(HTTPException) as token_invalido:
            ObtenerUsuarioAutenticado(sesion="token-inexistente")
        self.assertEqual(token_invalido.exception.status_code, 401)

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE LOGIN
    def test_documentacion_openapi_login(self):
        esquema = app.openapi()
        ruta = "/api/Usuarios/login"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

        post_doc = esquema["paths"][ruta]["post"]
        self.assertIn("summary", post_doc)
        self.assertIn("description", post_doc)
        for codigo in ["200", "401", "403", "500"]:
            self.assertIn(codigo, post_doc["responses"])


# PRUEBAS UNITARIAS PARA CERRAR SESIÓN EN EL SISTEMA
class TestLogoutUsuarios(unittest.TestCase):

    # PREPARAR ESTADO LIMPIO ANTES DE CADA PRUEBA
    def setUp(self):
        usuarioRepositorio.usuarios.clear()
        usuarioRepositorio.sesiones.clear()

        self.superadministrador = {
            "id": 1,
            "nombreUsuario": "superadmin",
            "esSuperadministrador": True
        }

        RegistrarUsuarioAPI(
            UsuarioRegistro(
                nombre="Laura Gomez",
                identificacion="123456789",
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            self.superadministrador
        )

    # CASO 1 Y 2: CIERRE DE SESIÓN EXITOSO Y BLOQUEO DE ACCESO POSTERIOR
    def test_cierre_sesion_exitoso_y_bloqueo_posterior(self):
        IniciarSesionAPI(
            datos=UsuarioLogin(
                nombreUsuario="laura.gomez",
                contrasena="ClaveSegura123*"
            ),
            response=Response()
        )
        token = next(iter(usuarioRepositorio.sesiones.keys()))

        # VERIFICAR QUE LA SESIÓN ESTÁ ACTIVA ANTES DE CERRAR
        usuario_activo = ObtenerUsuarioAutenticado(sesion=token)
        self.assertEqual(usuario_activo["nombreUsuario"], "laura.gomez")

        resp_logout = Response()
        resultado = CerrarSesionAPI(response=resp_logout, sesion=token)

        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["message"], "Sesión cerrada correctamente")
        self.assertEqual(len(usuarioRepositorio.sesiones), 0)
        self.assertIn("sesion=", resp_logout.headers.get("set-cookie", ""))

        # VERIFICAR QUE NO SE PUEDE ACCEDER CON LA SESIÓN FINALIZADA
        with self.assertRaises(HTTPException) as contexto:
            ObtenerUsuarioAutenticado(sesion=token)
        self.assertEqual(contexto.exception.status_code, 401)

    # CASO 3: SOLICITUD DE CIERRE SIN UNA SESIÓN ACTIVA
    def test_cierre_sesion_sin_sesion_activa(self):
        resp_logout = Response()
        resultado = CerrarSesionAPI(response=resp_logout, sesion=None)

        self.assertTrue(resultado["success"])
        self.assertEqual(resultado["message"], "Sesión cerrada correctamente")
        self.assertIn("sesion=", resp_logout.headers.get("set-cookie", ""))

    # CASO 4: ERROR DURANTE EL CIERRE DE SESIÓN
    @patch(
        "microservicios.usuarios.repositorio.usuarioRepositorio.EliminarSesionRepositorio",
        side_effect=RuntimeError("Error simulado al eliminar sesión")
    )
    def test_error_durante_cierre_sesion(self, mock_eliminar):
        respuesta = CerrarSesionAPI(
            response=Response(),
            sesion="token-activo"
        )
        cuerpo = json.loads(respuesta.body.decode("utf-8"))

        self.assertEqual(respuesta.status_code, 500)
        self.assertFalse(cuerpo["success"])
        self.assertEqual(cuerpo["message"], "No fue posible cerrar la sesión")

    # DOCUMENTACIÓN OPENAPI / SWAGGER DEL ENDPOINT DE LOGOUT
    def test_documentacion_openapi_logout(self):
        esquema = app.openapi()
        ruta = "/api/Usuarios/logout"
        self.assertIn(ruta, esquema["paths"])
        self.assertIn("post", esquema["paths"][ruta])

        post_doc = esquema["paths"][ruta]["post"]
        self.assertIn("summary", post_doc)
        self.assertIn("description", post_doc)
        self.assertIn("200", post_doc["responses"])
        self.assertIn("500", post_doc["responses"])


if __name__ == "__main__":
    unittest.main()
