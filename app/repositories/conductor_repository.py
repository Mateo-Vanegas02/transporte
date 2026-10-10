from typing import Any, Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConductorHasVehiculosException,
    LicenciaAlreadyExistsException,
)
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.schemas.conductor import ConductorCreate


class ConductorRepository:
    """
    Repositorio para Conductor.
    Encapsula el acceso a datos y traduce violaciones de integridad
    a excepciones de dominio.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, id_conductor: int) -> Optional[Conductor]:
        stmt = select(Conductor).where(Conductor.id_conductor == id_conductor)
        return self.db.scalars(stmt).first()

    def get_by_licencia(self, licencia: str) -> Optional[Conductor]:
        stmt = select(Conductor).where(Conductor.licencia == licencia)
        return self.db.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Conductor]:
        stmt = select(Conductor).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def count_vehiculos(self, id_conductor: int) -> int:
        """Cuenta la cantidad de vehículos asignados a un conductor."""
        stmt = select(func.count(Vehiculo.id_vehiculo)).where(
            Vehiculo.id_conductor == id_conductor
        )
        return self.db.scalar(stmt) or 0

    def get_vehiculos(self, id_conductor: int) -> Sequence[Vehiculo]:
        """Obtiene la lista de vehículos asignados al conductor."""
        stmt = select(Vehiculo).where(Vehiculo.id_conductor == id_conductor)
        return self.db.scalars(stmt).all()

    def create(self, conductor_in: ConductorCreate) -> Conductor:
        conductor = Conductor(
            nombre=conductor_in.nombre,
            licencia=conductor_in.licencia,
            telefono=conductor_in.telefono,
        )
        try:
            self.db.add(conductor)
            self.db.commit()
            self.db.refresh(conductor)
            return conductor
        except IntegrityError as err:
            self.db.rollback()
            if "licencia" in str(err).lower():
                raise LicenciaAlreadyExistsException(conductor_in.licencia) from err
            raise

    def update(
        self,
        conductor: Conductor,
        update_data: dict[str, Any],
    ) -> Conductor:
        for field, value in update_data.items():
            setattr(conductor, field, value)

        try:
            self.db.commit()
            self.db.refresh(conductor)
            return conductor
        except IntegrityError as err:
            self.db.rollback()
            if "licencia" in str(err).lower():
                raise LicenciaAlreadyExistsException(
                    update_data.get("licencia", conductor.licencia)
                ) from err
            raise

    def delete(self, conductor: Conductor) -> None:
        try:
            self.db.delete(conductor)
            self.db.commit()
        except IntegrityError as err:
            self.db.rollback()
            raise ConductorHasVehiculosException(conductor.id_conductor) from err
