from collections.abc import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.conductor_repository import ConductorRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.repositories.viaje_repository import ViajeRepository
from app.services.conductor_service import ConductorService
from app.services.vehiculo_service import VehiculoService
from app.services.viaje_service import ViajeService


def get_db() -> Generator[Session, None, None]:
    """
    Generador de sesión de base de datos por petición HTTP.
    Garantiza que la sesión se cierre al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_conductor_service(db: Session = Depends(get_db)) -> ConductorService:
    """Inyección de dependencias para ConductorService."""
    repo = ConductorRepository(db)
    return ConductorService(repo)


def get_vehiculo_service(db: Session = Depends(get_db)) -> VehiculoService:
    """Inyección de dependencias para VehiculoService."""
    vehiculo_repo = VehiculoRepository(db)
    conductor_repo = ConductorRepository(db)
    return VehiculoService(vehiculo_repo, conductor_repo)


def get_viaje_service(db: Session = Depends(get_db)) -> ViajeService:
    """Inyección de dependencias para ViajeService."""
    viaje_repo = ViajeRepository(db)
    vehiculo_repo = VehiculoRepository(db)
    return ViajeService(viaje_repo, vehiculo_repo)
