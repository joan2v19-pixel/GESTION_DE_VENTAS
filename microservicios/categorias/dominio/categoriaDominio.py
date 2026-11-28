
from microservicios.categorias.repositorio import categoriaRepositorio


# REGISTRAR UNA CATEGORÍA
def RegistrarCategoriaDominio(datos_categoria: dict):

    # VERIFICAR SI YA EXISTE UNA CATEGORÍA CON EL MISMO NOMBRE
    categoria_existente = categoriaRepositorio.ObtenerCategoriaPorNombreRepositorio(
        datos_categoria["nombre"]
    )

    if categoria_existente:
        raise ValueError("LA CATEGORÍA YA SE ENCUENTRA REGISTRADA.")

    # REGISTRAR LA CATEGORÍA
    return categoriaRepositorio.RegistrarCategoriaRepositorio(datos_categoria)



# CONSULTAR TODAS LAS CATEGORÍAS
def ConsultarCategoriasDominio():
    return categoriaRepositorio.ConsultarCategoriasRepositorio()


# CONSULTAR UNA CATEGORÍA POR ID
def ObtenerCategoriaPorIdDominio(id: int):
    return categoriaRepositorio.ObtenerCategoriaPorIdRepositorio(id)



# ACTUALIZAR UNA CATEGORÍA
def ActualizarCategoriaDominio(id: int, datos_categoria: dict):

    # VERIFICAR QUE LA CATEGORÍA EXISTA
    categoria_existente = categoriaRepositorio.ObtenerCategoriaPorIdRepositorio(id)

    if categoria_existente is None:
        raise LookupError("LA CATEGORÍA SELECCIONADA NO EXISTE.")

    # FILTRAR CAMPOS CON VALOR POR DEFECTO 'string' PARA NO MODIFICARLOS
    datos_filtrados = {
        clave: valor
        for clave, valor in datos_categoria.items()
        if not (isinstance(valor, str) and valor.strip().lower() == "string")
    }

    # VERIFICAR QUE EL NOMBRE NO PERTENEZCA A OTRA CATEGORÍA
    if "nombre" in datos_filtrados:
        categoria_nombre = categoriaRepositorio.ObtenerCategoriaPorNombreRepositorio(
            datos_filtrados["nombre"]
        )

        if categoria_nombre and categoria_nombre["id"] != id:
            raise ValueError("EL NOMBRE YA SE ENCUENTRA REGISTRADO EN OTRA CATEGORÍA.")

    # ACTUALIZAR LA CATEGORÍA
    return categoriaRepositorio.ActualizarCategoriaRepositorio(id, datos_filtrados)
