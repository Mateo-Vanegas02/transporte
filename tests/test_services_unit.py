from datetime import date
from unittest.mock import MagicMock
import pytest

from app.core.exceptions import (
    ConductorHasVehiculosException,
    ConductorNotFoundException,
    LicenciaAlreadyExistsException,
    PlacaAlreadyExistsException,
    VehiculoHasViajesException,
    VehiculoNotFoundException,
)
from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.viaje import Viaje
from app.schemas.conductor import ConductorCreate
from app.schemas.vehiculo import VehiculoCreate
from app.schemas.viaje import ViajeCreate
from app.services.conductor_service import ConductorService
from app.services.vehiculo_service import VehiculoService
from app.services.viaje_service import ViajeService


def test_conductor_service_create_duplicate_licencia_raises_exception() -> None:
    mock_repo = MagicMock()
    mock_repo.get_by_licencia.return_value = Conductor(
        id_conductor=1,
        nombre="Existente",
        licencia="LIC-MOCK",
        telefono="123",
    )
    service = ConductorService(mock_repo)

    with pytest.raises(LicenciaAlreadyExistsException):
        service.create_conductor(
            ConductorCreate(
                nombre="Nuevo",
                licencia="LIC-MOCK",
                telefono="456",
            )
        )


def test_conductor_service_delete_with_vehiculos_raises_exception() -> None:
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = Conductor(
        id_conductor=1,
        nombre="Existente",
        licencia="L-1",
        telefono="123",
    )
    mock_repo.count_vehiculos.return_value = 2  # Tiene 2 vehículos asociados
    service = ConductorService(mock_repo)

    with pytest.raises(ConductorHasVehiculosException):
        service.delete_conductor(1)


def test_vehiculo_service_create_non_existent_conductor_raises_exception() -> None:
    mock_vehiculo_repo = MagicMock()
    mock_conductor_repo = MagicMock()
    mock_conductor_repo.get_by_id.return_value = None  # Conductor no existe

    service = VehiculoService(mock_vehiculo_repo, mock_conductor_repo)

    with pytest.raises(ConductorNotFoundException):
        service.create_vehiculo(
            VehiculoCreate(
                placa="XYZ123",
                modelo="Camioneta",
                id_conductor=99,
            )
        )


def test_vehiculo_service_create_duplicate_placa_raises_exception() -> None:
    mock_vehiculo_repo = MagicMock()
    mock_conductor_repo = MagicMock()
    mock_conductor_repo.get_by_id.return_value = Conductor(
        id_conductor=1,
        nombre="Existe",
        licencia="L",
        telefono="T",
    )
    mock_vehiculo_repo.get_by_placa.return_value = Vehiculo(
        id_vehiculo=10,
        placa="XYZ123",
        modelo="M",
        id_conductor=1,
    )

    service = VehiculoService(mock_vehiculo_repo, mock_conductor_repo)

    with pytest.raises(PlacaAlreadyExistsException):
        service.create_vehiculo(
            VehiculoCreate(
                placa="XYZ123",
                modelo="Camioneta",
                id_conductor=1,
            )
        )


def test_vehiculo_service_delete_with_viajes_raises_exception() -> None:
    mock_vehiculo_repo = MagicMock()
    mock_conductor_repo = MagicMock()
    mock_vehiculo_repo.get_by_id.return_value = Vehiculo(
        id_vehiculo=10,
        placa="AAA",
        modelo="B",
        id_conductor=1,
    )
    mock_vehiculo_repo.count_viajes.return_value = 3  # Tiene 3 viajes asociados

    service = VehiculoService(mock_vehiculo_repo, mock_conductor_repo)

    with pytest.raises(VehiculoHasViajesException):
        service.delete_vehiculo(10)


def test_viaje_service_create_non_existent_vehiculo_raises_exception() -> None:
    mock_viaje_repo = MagicMock()
    mock_vehiculo_repo = MagicMock()
    mock_vehiculo_repo.get_by_id.return_value = None  # Vehículo no existe

    service = ViajeService(mock_viaje_repo, mock_vehiculo_repo)

    with pytest.raises(VehiculoNotFoundException):
        service.create_viaje(
            ViajeCreate(
                destino="Rionegro",
                fecha=date(2026, 10, 20),
                id_vehiculo=888,
            )
        )


def test_viaje_service_list_detalles_maps_correctly() -> None:
    mock_viaje_repo = MagicMock()
    mock_vehiculo_repo = MagicMock()

    conductor = Conductor(
        id_conductor=1,
        nombre="Conductor Test",
        licencia="L",
        telefono="T",
    )
    vehiculo = Vehiculo(
        id_vehiculo=1,
        placa="TEST01",
        modelo="Duster",
        id_conductor=1,
    )
    vehiculo.conductor = conductor

    viaje = Viaje(
        id_viaje=100,
        destino="Medellin",
        fecha=date(2026, 10, 20),
        id_vehiculo=1,
    )
    viaje.vehiculo = vehiculo

    mock_viaje_repo.get_detalles.return_value = [viaje]
    service = ViajeService(mock_viaje_repo, mock_vehiculo_repo)

    detalles = service.list_detalles()
    assert len(detalles) == 1
    assert detalles[0].id_viaje == 100
    assert detalles[0].conductor == "Conductor Test"
    assert detalles[0].placa == "TEST01"
