
from microservicios.categorias.repositorio import categoriaRepositorio


# Registrar una categoría
def RegistrarCategoriaDominio(datos_categoria: dict):

    # Verificar si ya existe una categoría con el mismo nombre
    categoria_existente = categoriaRepositorio.ObtenerCategoriaPorNombreRepositorio(
        datos_categoria["nombre"]
    )

    if categoria_existente:
        raise ValueError("LA CATEGORÍA YA SE ENCUENTRA REGISTRADA.")

    # Registrar la categoría
    return categoriaRepositorio.RegistrarCategoriaRepositorio(datos_categoria)
