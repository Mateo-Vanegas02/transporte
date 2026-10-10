from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conductor import Conductor
from app.models.vehiculo import Vehiculo
from app.models.viaje import Viaje
from scripts.seed import seed_database


def test_seed_database_is_idempotent(db_session: Session) -> None:
    """
    Verifica que la ejecución del seed sea 100% idempotente:
    correrlo dos veces consecutivas debe mantener exactamente
    5 conductores, 5 vehículos y 8 viajes sin duplicados.
    """
    # Primera ejecución sobre base limpia
    seed_database(session=db_session)

    conductores_1 = list(db_session.scalars(select(Conductor)).all())
    vehiculos_1 = list(db_session.scalars(select(Vehiculo)).all())
    viajes_1 = list(db_session.scalars(select(Viaje)).all())

    assert len(conductores_1) == 5
    assert len(vehiculos_1) == 5
    assert len(viajes_1) == 8

    # Segunda ejecución consecutiva
    seed_database(session=db_session)

    conductores_2 = list(db_session.scalars(select(Conductor)).all())
    vehiculos_2 = list(db_session.scalars(select(Vehiculo)).all())
    viajes_2 = list(db_session.scalars(select(Viaje)).all())

    assert len(conductores_2) == 5
    assert len(vehiculos_2) == 5
    assert len(viajes_2) == 8
