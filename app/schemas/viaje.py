from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class ViajeBase(BaseModel):
    """Atributos base para la entidad Viaje."""

    destino: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Destino del viaje",
        examples=["Aeropuerto José María Córdova"],
    )
    fecha: date = Field(
        ...,
        description="Fecha programada del viaje (formato YYYY-MM-DD)",
        examples=["2026-10-15"],
    )
    id_vehiculo: int = Field(
        ...,
        ge=1,
        description="ID del vehículo asignado (FK)",
        examples=[1],
    )


class ViajeCreate(ViajeBase):
    """Esquema para creación de Viaje."""

    pass


class ViajeUpdate(BaseModel):
    """
    Esquema para actualización de Viaje (soporta PATCH parcial y PUT total).
    Rechaza valores 'null' explícitos para proteger columnas NOT NULL en base de datos.
    """

    destino: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Destino del viaje",
    )
    fecha: Optional[date] = Field(
        None,
        description="Fecha programada del viaje",
    )
    id_vehiculo: Optional[int] = Field(
        None,
        ge=1,
        description="ID del vehículo asignado (FK)",
    )

    @field_validator("destino", "fecha", "id_vehiculo", mode="before")
    @classmethod
    def reject_null(cls, value: Any, info: ValidationInfo) -> Any:
        if value is None:
            raise ValueError(f"El campo '{info.field_name}' no puede ser nulo.")
        return value


class ViajeRead(ViajeBase):
    """Esquema de respuesta para Viaje."""

    id_viaje: int = Field(..., description="Identificador único del viaje")

    model_config = ConfigDict(from_attributes=True)


class ViajeDetalleRead(BaseModel):
    """
    Esquema de respuesta para el reporte consolidado de viaje,
    incluyendo los datos de las 3 tablas relacionadas.
    """

    id_viaje: int = Field(..., description="ID del viaje")
    destino: str = Field(..., description="Destino del viaje")
    fecha: date = Field(..., description="Fecha del viaje")
    placa: str = Field(..., description="Placa del vehículo")
    conductor: str = Field(..., description="Nombre del conductor a cargo")
    modelo: Optional[str] = Field(None, description="Modelo del vehículo")

    model_config = ConfigDict(from_attributes=True)
