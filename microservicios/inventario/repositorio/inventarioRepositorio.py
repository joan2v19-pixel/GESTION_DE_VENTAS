# LISTA PARA ALMACENAR LOS REGISTROS DE INVENTARIO EN MEMORIA
inventarios = []


# REGISTRAR EXISTENCIAS INICIALES DE UN PRODUCTO EN EL REPOSITORIO
def RegistrarExistenciasInicialesRepositorio(datos_inventario: dict) -> dict:

    # CONSTRUIR EL REGISTRO DE INVENTARIO ASOCIADO AL PRODUCTO
    nuevo_inventario = {
        "id": len(inventarios) + 1,
        "producto_id": datos_inventario["producto_id"],
        "cantidad_inicial": datos_inventario["cantidad_inicial"]
    }

    inventarios.append(nuevo_inventario)

    return nuevo_inventario


# CONSULTAR EL INVENTARIO DE UN PRODUCTO POR SU IDENTIFICADOR
def ObtenerInventarioPorProductoIdRepositorio(producto_id: int) -> dict | None:

    for inventario in inventarios:
        if inventario["producto_id"] == producto_id:
            return inventario

    return None
