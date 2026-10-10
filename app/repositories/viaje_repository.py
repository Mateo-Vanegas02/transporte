from datetime import date
from typing import Any, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import VehiculoNotFoundException
from app.models.vehiculo import Vehiculo
from app.models.viaje import Viaje
from app.schemas.viaje import ViajeCreate


class ViajeRepository:
    """
    Repositorio para Viaje.
    Encapsula consultas con filtros, carga impaciente (joinedload) para reportes,
    y traducción de errores de integridad referencial.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, id_viaje: int) -> Optional[Viaje]:
        stmt = select(Viaje).where(Viaje.id_viaje == id_viaje)
        return self.db.scalars(stmt).first()

    def get_filtered(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        destino: Optional[str] = None,
        id_vehiculo: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Viaje]:
        """Consulta viajes con filtros opcionales y paginación."""
        stmt = select(Viaje)
        if fecha_desde is not None:
            stmt = stmt.where(Viaje.fecha >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(Viaje.fecha <= fecha_hasta)
        if destino is not None and destino.strip() != "":
            stmt = stmt.where(Viaje.destino.ilike(f"%{destino.strip()}%"))
        if id_vehiculo is not None:
            stmt = stmt.where(Viaje.id_vehiculo == id_vehiculo)

        stmt = stmt.offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def get_detalles(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Viaje]:
        """
        Consulta optimizada con joinedload para unir Viaje -> Vehiculo -> Conductor
        en una sola consulta SQL, previniendo el problema de N+1 queries.
        """
        stmt = (
            select(Viaje)
            .options(joinedload(Viaje.vehiculo).joinedload(Vehiculo.conductor))
            .offset(skip)
            .limit(limit)
        )
        return self.db.scalars(stmt).unique().all()

    def create(self, viaje_in: ViajeCreate) -> Viaje:
        viaje = Viaje(
            destino=viaje_in.destino,
            fecha=viaje_in.fecha,
            id_vehiculo=viaje_in.id_vehiculo,
        )
        try:
            self.db.add(viaje)
            self.db.commit()
            self.db.refresh(viaje)
            return viaje
        except IntegrityError as err:
            self.db.rollback()
            err_str = str(err).lower()
            if "foreign key" in err_str or "id_vehiculo" in err_str:
                raise VehiculoNotFoundException(viaje_in.id_vehiculo) from err
            raise

    def update(
        self,
        viaje: Viaje,
        update_data: dict[str, Any],
    ) -> Viaje:
        for field, value in update_data.items():
            setattr(viaje, field, value)

        try:
            self.db.commit()
            self.db.refresh(viaje)
            return viaje
        except IntegrityError as err:
            self.db.rollback()
            err_str = str(err).lower()
            if "foreign key" in err_str or "id_vehiculo" in err_str:
                raise VehiculoNotFoundException(
                    update_data.get("id_vehiculo", viaje.id_vehiculo)
                ) from err
            raise

    def delete(self, viaje: Viaje) -> None:
        self.db.delete(viaje)
        self.db.commit()
