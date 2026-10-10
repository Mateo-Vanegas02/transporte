from typing import Any, Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConductorNotFoundException,
    PlacaAlreadyExistsException,
    VehiculoHasViajesException,
)
from app.models.vehiculo import Vehiculo
from app.models.viaje import Viaje
from app.schemas.vehiculo import VehiculoCreate


class VehiculoRepository:
    """
    Repositorio para Vehiculo.
    Encapsula el acceso a datos y traduce violaciones de integridad
    a excepciones de dominio.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, id_vehiculo: int) -> Optional[Vehiculo]:
        stmt = select(Vehiculo).where(Vehiculo.id_vehiculo == id_vehiculo)
        return self.db.scalars(stmt).first()

    def get_by_placa(self, placa: str) -> Optional[Vehiculo]:
        stmt = select(Vehiculo).where(Vehiculo.placa == placa)
        return self.db.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Vehiculo]:
        stmt = select(Vehiculo).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def count_viajes(self, id_vehiculo: int) -> int:
        """Cuenta la cantidad de viajes asignados a un vehículo."""
        stmt = select(func.count(Viaje.id_viaje)).where(
            Viaje.id_vehiculo == id_vehiculo
        )
        return self.db.scalar(stmt) or 0

    def get_viajes(self, id_vehiculo: int) -> Sequence[Viaje]:
        """Obtiene la lista de viajes asignados al vehículo."""
        stmt = select(Viaje).where(Viaje.id_vehiculo == id_vehiculo)
        return self.db.scalars(stmt).all()

    def create(self, vehiculo_in: VehiculoCreate) -> Vehiculo:
        vehiculo = Vehiculo(
            placa=vehiculo_in.placa,
            modelo=vehiculo_in.modelo,
            id_conductor=vehiculo_in.id_conductor,
        )
        try:
            self.db.add(vehiculo)
            self.db.commit()
            self.db.refresh(vehiculo)
            return vehiculo
        except IntegrityError as err:
            self.db.rollback()
            err_str = str(err).lower()
            if "placa" in err_str:
                raise PlacaAlreadyExistsException(vehiculo_in.placa) from err
            if "foreign key" in err_str or "id_conductor" in err_str:
                raise ConductorNotFoundException(vehiculo_in.id_conductor) from err
            raise

    def update(
        self,
        vehiculo: Vehiculo,
        update_data: dict[str, Any],
    ) -> Vehiculo:
        for field, value in update_data.items():
            setattr(vehiculo, field, value)

        try:
            self.db.commit()
            self.db.refresh(vehiculo)
            return vehiculo
        except IntegrityError as err:
            self.db.rollback()
            err_str = str(err).lower()
            if "placa" in err_str:
                raise PlacaAlreadyExistsException(
                    update_data.get("placa", vehiculo.placa)
                ) from err
            if "foreign key" in err_str or "id_conductor" in err_str:
                raise ConductorNotFoundException(
                    update_data.get("id_conductor", vehiculo.id_conductor)
                ) from err
            raise

    def delete(self, vehiculo: Vehiculo) -> None:
        try:
            self.db.delete(vehiculo)
            self.db.commit()
        except IntegrityError as err:
            self.db.rollback()
            raise VehiculoHasViajesException(vehiculo.id_vehiculo) from err
