from typing import Sequence

from app.core.exceptions import (
    ConductorNotFoundException,
    PlacaAlreadyExistsException,
    VehiculoHasViajesException,
    VehiculoNotFoundException,
)
from app.models.vehiculo import Vehiculo
from app.models.viaje import Viaje
from app.repositories.conductor_repository import ConductorRepository
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate


class VehiculoService:
    """Lógica de negocio y reglas para la gestión de Vehículos."""

    def __init__(
        self,
        vehiculo_repo: VehiculoRepository,
        conductor_repo: ConductorRepository,
    ) -> None:
        self.vehiculo_repo = vehiculo_repo
        self.conductor_repo = conductor_repo

    def get_by_id(self, id_vehiculo: int) -> Vehiculo:
        vehiculo = self.vehiculo_repo.get_by_id(id_vehiculo)
        if not vehiculo:
            raise VehiculoNotFoundException(id_vehiculo)
        return vehiculo

    def list_vehiculos(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Vehiculo]:
        return self.vehiculo_repo.get_all(skip=skip, limit=limit)

    def get_viajes_by_vehiculo(
        self,
        id_vehiculo: int,
    ) -> Sequence[Viaje]:
        """Retorna los viajes del vehículo previa verificación de existencia."""
        self.get_by_id(id_vehiculo)
        return self.vehiculo_repo.get_viajes(id_vehiculo)

    def create_vehiculo(self, vehiculo_in: VehiculoCreate) -> Vehiculo:
        # Validación de existencia del conductor asignado
        conductor = self.conductor_repo.get_by_id(vehiculo_in.id_conductor)
        if not conductor:
            raise ConductorNotFoundException(vehiculo_in.id_conductor)

        # Validación preventiva de unicidad de placa
        existing_placa = self.vehiculo_repo.get_by_placa(vehiculo_in.placa)
        if existing_placa:
            raise PlacaAlreadyExistsException(vehiculo_in.placa)

        return self.vehiculo_repo.create(vehiculo_in)

    def update_vehiculo(
        self,
        id_vehiculo: int,
        vehiculo_in: VehiculoUpdate,
    ) -> Vehiculo:
        vehiculo = self.get_by_id(id_vehiculo)

        update_data = vehiculo_in.model_dump(exclude_unset=True)
        if not update_data:
            return vehiculo

        # Si se actualiza el conductor, validar su existencia
        if "id_conductor" in update_data:
            conductor = self.conductor_repo.get_by_id(update_data["id_conductor"])
            if not conductor:
                raise ConductorNotFoundException(update_data["id_conductor"])

        # Si se actualiza la placa, validar unicidad
        if "placa" in update_data and update_data["placa"] != vehiculo.placa:
            existing_placa = self.vehiculo_repo.get_by_placa(update_data["placa"])
            if existing_placa and existing_placa.id_vehiculo != id_vehiculo:
                raise PlacaAlreadyExistsException(update_data["placa"])

        return self.vehiculo_repo.update(vehiculo, update_data)

    def delete_vehiculo(self, id_vehiculo: int) -> None:
        vehiculo = self.get_by_id(id_vehiculo)

        # Regla de negocio: no eliminar vehículos con viajes asociados
        if self.vehiculo_repo.count_viajes(id_vehiculo) > 0:
            raise VehiculoHasViajesException(id_vehiculo)

        self.vehiculo_repo.delete(vehiculo)
