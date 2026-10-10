from app.schemas.conductor import (
    ConductorBase,
    ConductorCreate,
    ConductorRead,
    ConductorUpdate,
)
from app.schemas.vehiculo import (
    VehiculoBase,
    VehiculoCreate,
    VehiculoRead,
    VehiculoUpdate,
)
from app.schemas.viaje import (
    ViajeBase,
    ViajeCreate,
    ViajeDetalleRead,
    ViajeRead,
    ViajeUpdate,
)

__all__ = [
    "ConductorBase",
    "ConductorCreate",
    "ConductorUpdate",
    "ConductorRead",
    "VehiculoBase",
    "VehiculoCreate",
    "VehiculoUpdate",
    "VehiculoRead",
    "ViajeBase",
    "ViajeCreate",
    "ViajeUpdate",
    "ViajeRead",
    "ViajeDetalleRead",
]
