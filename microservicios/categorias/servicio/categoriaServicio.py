
from microservicios.categorias.dominio import categoriaDominio


# Registrar una categoría
def RegistrarCategoriaServicio(datos_categoria: dict):
    return categoriaDominio.RegistrarCategoriaDominio(datos_categoria)


# Consultar todas las categorías
def ConsultarCategoriasServicio():
    return categoriaDominio.ConsultarCategoriasDominio()


# Consultar una categoría por ID
def ObtenerCategoriaPorIdServicio(id: int):
    return categoriaDominio.ObtenerCategoriaPorIdDominio(id)


# Actualizar una categoría
def ActualizarCategoriaServicio(id: int, datos_categoria: dict):
    return categoriaDominio.ActualizarCategoriaDominio(id, datos_categoria)
