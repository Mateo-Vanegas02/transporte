"""
Script de inicialización y carga de datos semilla (idempotente)
para la base de datos de transporte.
Carga 5 conductores, 5 vehículos y 8 viajes en Medellín.
"""

from datetime import date
import os
import sys
from typing import Optional

# Asegura que 'app' esté disponible independientemente del directorio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.conductor import Conductor  # noqa: E402
from app.models.vehiculo import Vehiculo  # noqa: E402
from app.models.viaje import Viaje  # noqa: E402

CONDUCTORES_DATA = [
    {
        "nombre": "Carlos Pérez",
        "licencia": "LIC-1001",
        "telefono": "3001112233",
    },
    {
        "nombre": "María Gómez",
        "licencia": "LIC-1002",
        "telefono": "3012223344",
    },
    {
        "nombre": "Andrés Torres",
        "licencia": "LIC-1003",
        "telefono": "3023334455",
    },
    {
        "nombre": "Laura Ramírez",
        "licencia": "LIC-1004",
        "telefono": "3034445566",
    },
    {
        "nombre": "Juan Martínez",
        "licencia": "LIC-1005",
        "telefono": "3045556677",
    },
]

VEHICULOS_DATA = [
    {
        "placa": "ABC123",
        "modelo": "Chevrolet Spark 2020",
        "licencia_conductor": "LIC-1001",
    },
    {
        "placa": "DEF456",
        "modelo": "Renault Logan 2019",
        "licencia_conductor": "LIC-1002",
    },
    {
        "placa": "GHI789",
        "modelo": "Kia Picanto 2021",
        "licencia_conductor": "LIC-1003",
    },
    {
        "placa": "JKL012",
        "modelo": "Mazda 2 2022",
        "licencia_conductor": "LIC-1004",
    },
    {
        "placa": "MNO345",
        "modelo": "Hyundai i10 2018",
        "licencia_conductor": "LIC-1005",
    },
]

VIAJES_DATA = [
    {
        "destino": "Aeropuerto José María Córdova",
        "fecha": date(2026, 10, 1),
        "placa_vehiculo": "ABC123",
    },
    {
        "destino": "Terminal del Norte",
        "fecha": date(2026, 10, 2),
        "placa_vehiculo": "DEF456",
    },
    {
        "destino": "Centro Comercial El Tesoro",
        "fecha": date(2026, 10, 3),
        "placa_vehiculo": "GHI789",
    },
    {
        "destino": "Parque Arví",
        "fecha": date(2026, 10, 4),
        "placa_vehiculo": "JKL012",
    },
    {
        "destino": "Universidad de Antioquia",
        "fecha": date(2026, 10, 5),
        "placa_vehiculo": "MNO345",
    },
    {
        "destino": "Terminal del Sur",
        "fecha": date(2026, 10, 6),
        "placa_vehiculo": "ABC123",
    },
    {
        "destino": "Estadio Atanasio Girardot",
        "fecha": date(2026, 10, 7),
        "placa_vehiculo": "DEF456",
    },
    {
        "destino": "Plaza Mayor",
        "fecha": date(2026, 10, 8),
        "placa_vehiculo": "GHI789",
    },
]


def seed_database(session: Optional[Session] = None) -> None:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        print("[INFO] Iniciando carga de datos semilla...")

        # 1. Cargar Conductores
        conductores_map: dict[str, Conductor] = {}
        for c_data in CONDUCTORES_DATA:
            stmt = select(Conductor).where(Conductor.licencia == c_data["licencia"])
            conductor = session.scalars(stmt).first()
            if not conductor:
                conductor = Conductor(
                    nombre=c_data["nombre"],
                    licencia=c_data["licencia"],
                    telefono=c_data["telefono"],
                )
                session.add(conductor)
                session.commit()
                session.refresh(conductor)
                print(
                    f"  [+] Conductor creado: {conductor.nombre} "
                    f"({conductor.licencia})"
                )
            else:
                print(
                    f"  [=] Conductor existente: {conductor.nombre} "
                    f"({conductor.licencia})"
                )
            conductores_map[conductor.licencia] = conductor

        # 2. Cargar Vehículos
        vehiculos_map: dict[str, Vehiculo] = {}
        for v_data in VEHICULOS_DATA:
            stmt = select(Vehiculo).where(Vehiculo.placa == v_data["placa"])
            vehiculo = session.scalars(stmt).first()
            conductor = conductores_map[v_data["licencia_conductor"]]
            if not vehiculo:
                vehiculo = Vehiculo(
                    placa=v_data["placa"],
                    modelo=v_data["modelo"],
                    id_conductor=conductor.id_conductor,
                )
                session.add(vehiculo)
                session.commit()
                session.refresh(vehiculo)
                print(f"  [+] Vehículo creado: {vehiculo.placa} - {vehiculo.modelo}")
            else:
                print(f"  [=] Vehículo existente: {vehiculo.placa}")
            vehiculos_map[vehiculo.placa] = vehiculo

        # 3. Cargar Viajes
        for vj_data in VIAJES_DATA:
            vehiculo = vehiculos_map[vj_data["placa_vehiculo"]]
            stmt = select(Viaje).where(
                Viaje.destino == vj_data["destino"],
                Viaje.fecha == vj_data["fecha"],
                Viaje.id_vehiculo == vehiculo.id_vehiculo,
            )
            viaje = session.scalars(stmt).first()
            if not viaje:
                viaje = Viaje(
                    destino=vj_data["destino"],
                    fecha=vj_data["fecha"],
                    id_vehiculo=vehiculo.id_vehiculo,
                )
                session.add(viaje)
                session.commit()
                session.refresh(viaje)
                print(f"  [+] Viaje creado: {viaje.destino} ({viaje.fecha})")
            else:
                print(f"  [=] Viaje existente: {viaje.destino} ({viaje.fecha})")

        print("[OK] Carga de datos semilla finalizada exitosamente.")
    except Exception as exc:
        session.rollback()
        print(f"[ERROR] Error durante la carga semilla: {exc}")
        raise
    finally:
        if close_session:
            session.close()


if __name__ == "__main__":
    seed_database()
