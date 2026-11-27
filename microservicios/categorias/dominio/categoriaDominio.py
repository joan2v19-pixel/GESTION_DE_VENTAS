
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



# Consultar todas las categorías
def ConsultarCategoriasDominio():
    return categoriaRepositorio.ConsultarCategoriasRepositorio()


# Consultar una categoría por ID
def ObtenerCategoriaPorIdDominio(id: int):
    return categoriaRepositorio.ObtenerCategoriaPorIdRepositorio(id)



# Actualizar una categoría
def ActualizarCategoriaDominio(id: int, datos_categoria: dict):

    # Verificar que la categoría exista
    categoria_existente = categoriaRepositorio.ObtenerCategoriaPorIdRepositorio(id)

    if categoria_existente is None:
        raise LookupError("LA CATEGORÍA SELECCIONADA NO EXISTE.")

    datos_filtrados = {
        clave: valor
        for clave, valor in datos_categoria.items()
        if not (isinstance(valor, str) and valor.strip().lower() == "string")
    }

    # Verificar que el nombre no pertenezca a otra categoría
    if "nombre" in datos_filtrados:
        categoria_nombre = categoriaRepositorio.ObtenerCategoriaPorNombreRepositorio(
            datos_filtrados["nombre"]
        )

        if categoria_nombre and categoria_nombre["id"] != id:
            raise ValueError("EL NOMBRE YA SE ENCUENTRA REGISTRADO EN OTRA CATEGORÍA.")

    # Actualizar la categoría
    return categoriaRepositorio.ActualizarCategoriaRepositorio(id, datos_filtrados)
