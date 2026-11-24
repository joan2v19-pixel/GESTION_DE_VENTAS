
# Lista para almacenar las categorías en memoria
categorias = []


# Registrar una categoría
def RegistrarCategoriaRepositorio(datos_categoria: dict):

    nueva_categoria = {
        "id": len(categorias) + 1,
        **datos_categoria
    }

    categorias.append(nueva_categoria)

    return nueva_categoria


# Consultar una categoría por nombre
def ObtenerCategoriaPorNombreRepositorio(nombre: str):

    for categoria in categorias:
        if categoria["nombre"].lower() == nombre.lower():
            return categoria

    return None


# Consultar todas las categorías
def ConsultarCategoriasRepositorio():
    return categorias


# Consultar una categoría por ID
def ObtenerCategoriaPorIdRepositorio(id: int):

    for categoria in categorias:
        if categoria["id"] == id:
            return categoria

    return None
