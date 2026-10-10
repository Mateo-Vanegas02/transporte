from typing import Sequence

from app.core.exceptions import (
    ConductorHasVehiculosException,
    ConductorNotFoundException,
    LicenciaAlreadyExistsException,
)
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.repositories.conductor_repository import ConductorRepository
from app.schemas.conductor import ConductorCreate, ConductorUpdate


class ConductorService:
    """Lógica de negocio y reglas para la gestión de Conductores."""

    def __init__(self, conductor_repo: ConductorRepository) -> None:
        self.conductor_repo = conductor_repo

    def get_by_id(self, id_conductor: int) -> Conductor:
        conductor = self.conductor_repo.get_by_id(id_conductor)
        if not conductor:
            raise ConductorNotFoundException(id_conductor)
        return conductor

    def list_conductores(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Conductor]:
        return self.conductor_repo.get_all(skip=skip, limit=limit)

    def get_vehiculos_by_conductor(
        self,
        id_conductor: int,
    ) -> Sequence[Vehiculo]:
        """
        Retorna los vehículos asignados al conductor previa
        verificación de existencia.
        """
        self.get_by_id(id_conductor)
        return self.conductor_repo.get_vehiculos(id_conductor)

    def create_conductor(self, conductor_in: ConductorCreate) -> Conductor:
        # Validación preventiva de unicidad de licencia
        existing = self.conductor_repo.get_by_licencia(conductor_in.licencia)
        if existing:
            raise LicenciaAlreadyExistsException(conductor_in.licencia)

        return self.conductor_repo.create(conductor_in)

    def update_conductor(
        self,
        id_conductor: int,
        conductor_in: ConductorUpdate,
    ) -> Conductor:
        conductor = self.get_by_id(id_conductor)

        update_data = conductor_in.model_dump(exclude_unset=True)
        if not update_data:
            return conductor

        # Validación si la nueva licencia ya pertenece a otro conductor
        if "licencia" in update_data and update_data["licencia"] != conductor.licencia:
            existing = self.conductor_repo.get_by_licencia(update_data["licencia"])
            if existing and existing.id_conductor != id_conductor:
                raise LicenciaAlreadyExistsException(update_data["licencia"])

        return self.conductor_repo.update(conductor, update_data)

    def delete_conductor(self, id_conductor: int) -> None:
        conductor = self.get_by_id(id_conductor)

        # Regla de negocio: no eliminar conductores con vehículos asociados
        if self.conductor_repo.count_vehiculos(id_conductor) > 0:
            raise ConductorHasVehiculosException(id_conductor)

        self.conductor_repo.delete(conductor)
