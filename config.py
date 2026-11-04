import os
from dotenv import load_dotenv

load_dotenv()

# Configuración general
APP_NAME = os.getenv("APP_NAME", "Gestion de Ventas")
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Seguridad
SECRET_KEY = os.getenv("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada")