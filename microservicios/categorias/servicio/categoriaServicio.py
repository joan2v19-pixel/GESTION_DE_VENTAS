
from microservicios.categorias.dominio import categoriaDominio


# Registrar una categoría
def RegistrarCategoriaServicio(datos_categoria: dict):
    return categoriaDominio.RegistrarCategoriaDominio(datos_categoria)
