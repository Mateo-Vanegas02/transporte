from app.api.conductores import router as conductores_router
from app.api.vehiculos import router as vehiculos_router
from app.api.viajes import router as viajes_router

__all__ = [
    "conductores_router",
    "vehiculos_router",
    "viajes_router",
]
