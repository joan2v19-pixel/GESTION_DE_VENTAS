from fastapi import FastAPI

app = FastAPI(
    title="Proyecto Web Services",
    description="API desarrollada con arquitectura de microservicios",
    version="1.0.0"
)

@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido al proyecto Web Services",
        "estado": "Funcionando correctamente"
    }