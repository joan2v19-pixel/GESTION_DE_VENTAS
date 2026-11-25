# LISTA PARA ALMACENAR LOS PRODUCTOS EN MEMORIA
productos = []


# REGISTRAR UN NUEVO PRODUCTO EN EL REPOSITORIO
def RegistrarProductoRepositorio(datos_producto: dict) -> dict:

    # CONSTRUIR EL REGISTRO DEL PRODUCTO CON SU IDENTIFICADOR ÚNICO
    nuevo_producto = {
        "id": len(productos) + 1,
        "nombre": datos_producto["nombre"],
        "codigo": datos_producto["codigo"],
        "precio": datos_producto["precio"],
        "categoria_id": datos_producto["categoria_id"]
    }

    productos.append(nuevo_producto)

    return nuevo_producto


# CONSULTAR UN PRODUCTO POR SU CÓDIGO ÚNICO
def ObtenerProductoPorCodigoRepositorio(codigo: str) -> dict | None:

    for producto in productos:
        if producto["codigo"].lower() == codigo.lower():
            return producto

    return None


# CONSULTAR TODOS LOS PRODUCTOS REGISTRADOS
def ConsultarProductosRepositorio() -> list[dict]:
    return productos


# CONSULTAR UN PRODUCTO POR SU IDENTIFICADOR
def ObtenerProductoPorIdRepositorio(id: int) -> dict | None:

    for producto in productos:
        if producto["id"] == id:
            return producto

    return None
