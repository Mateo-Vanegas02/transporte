import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.conductores import router as conductores_router
from app.api.vehiculos import router as vehiculos_router
from app.api.viajes import router as viajes_router
from app.core.config import settings
from app.db.session import Base, engine

# Importamos modelos para registrar tablas en Base.metadata
from app.models import Conductor, Vehiculo, Viaje  # noqa: F401

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestión del ciclo de vida de la aplicación.
    El esquema de BD se gestiona formalmente con migraciones de Alembic.
    Solo ejecuta create_all si INIT_DB_ON_STARTUP está explícitamente activado.
    """
    if settings.INIT_DB_ON_STARTUP:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Tablas de base de datos creadas/verificadas.")
        except Exception as exc:
            logger.warning("No fue posible conectar a MySQL en el arranque: %s", exc)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "API REST profesional para el Sistema de Gestión de Transporte. "
        "Arquitectura por capas (Router -> Service -> Repository), "
        "FastAPI, SQLAlchemy 2.0 y MySQL."
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


# Registro de routers bajo el prefijo unificado /api/v1
app.include_router(conductores_router, prefix=settings.API_V1_STR)
app.include_router(vehiculos_router, prefix=settings.API_V1_STR)
app.include_router(viajes_router, prefix=settings.API_V1_STR)
