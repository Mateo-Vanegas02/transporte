from datetime import date
from typing import Optional, Sequence

from app.core.exceptions import (
    VehiculoNotFoundException,
    ViajeNotFoundException,
)
from app.models.viaje import Viaje
from app.repositories.vehiculo_repository import VehiculoRepository
from app.repositories.viaje_repository import ViajeRepository
from app.schemas.viaje import ViajeCreate, ViajeDetalleRead, ViajeUpdate


class ViajeService:
    """Lógica de negocio y reglas para la gestión de Viajes y reportes."""

    def __init__(
        self,
        viaje_repo: ViajeRepository,
        vehiculo_repo: VehiculoRepository,
    ) -> None:
        self.viaje_repo = viaje_repo
        self.vehiculo_repo = vehiculo_repo

    def get_by_id(self, id_viaje: int) -> Viaje:
        viaje = self.viaje_repo.get_by_id(id_viaje)
        if not viaje:
            raise ViajeNotFoundException(id_viaje)
        return viaje

    def list_viajes(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        destino: Optional[str] = None,
        id_vehiculo: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Viaje]:
        return self.viaje_repo.get_filtered(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            destino=destino,
            id_vehiculo=id_vehiculo,
            skip=skip,
            limit=limit,
        )

    def list_detalles(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ViajeDetalleRead]:
        """
        Retorna la vista consolidada del viaje, conductor y vehículo
        utilizando la consulta optimizada con joinedload.
        """
        viajes = self.viaje_repo.get_detalles(skip=skip, limit=limit)
        detalles: list[ViajeDetalleRead] = []
        for v in viajes:
            conductor_nombre = ""
            placa = ""
            modelo = None
            if v.vehiculo:
                placa = v.vehiculo.placa
                modelo = v.vehiculo.modelo
                if v.vehiculo.conductor:
                    conductor_nombre = v.vehiculo.conductor.nombre

            detalles.append(
                ViajeDetalleRead(
                    id_viaje=v.id_viaje,
                    destino=v.destino,
                    fecha=v.fecha,
                    placa=placa,
                    conductor=conductor_nombre,
                    modelo=modelo,
                )
            )
        return detalles

    def create_viaje(self, viaje_in: ViajeCreate) -> Viaje:
        # Validación de existencia del vehículo asignado
        vehiculo = self.vehiculo_repo.get_by_id(viaje_in.id_vehiculo)
        if not vehiculo:
            raise VehiculoNotFoundException(viaje_in.id_vehiculo)

        return self.viaje_repo.create(viaje_in)

    def update_viaje(
        self,
        id_viaje: int,
        viaje_in: ViajeUpdate,
    ) -> Viaje:
        viaje = self.get_by_id(id_viaje)

        update_data = viaje_in.model_dump(exclude_unset=True)
        if not update_data:
            return viaje

        # Si se actualiza el vehículo, validar su existencia
        if "id_vehiculo" in update_data:
            vehiculo = self.vehiculo_repo.get_by_id(update_data["id_vehiculo"])
            if not vehiculo:
                raise VehiculoNotFoundException(update_data["id_vehiculo"])

        return self.viaje_repo.update(viaje, update_data)

    def delete_viaje(self, id_viaje: int) -> None:
        viaje = self.get_by_id(id_viaje)
        self.viaje_repo.delete(viaje)
