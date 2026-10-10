import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.users import router as users_router
from app.core.config import settings
from app.db.session import Base, engine

# Importamos el modelo User para registrarlo en el metadata antes de create_all
from app.models.user import User  # noqa: F401

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestión del ciclo de vida de la aplicación.
    Al iniciar, crea automáticamente las tablas en la BD si no existen.
    En producción o evolución de esquemas se recomienda migrar con Alembic.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas de base de datos verificadas/creadas exitosamente.")
    except Exception as exc:
        logger.warning(
            "No fue posible conectar a MySQL para inicializar tablas en el "
            "arranque: %s. Asegúrate de que MySQL esté activo.",
            exc,
        )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "API REST profesional con arquitectura por capas "
        "(Router -> Service -> Repository), FastAPI y MySQL."
    ),
    lifespan=lifespan,
)


@app.get(
    "/health",
    tags=["Salud"],
    summary="Verificación de estado de la API",
)
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.PROJECT_NAME}


# Registro del router de usuarios
app.include_router(users_router)
