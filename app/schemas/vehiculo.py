from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class VehiculoBase(BaseModel):
    """Atributos base para la entidad Vehiculo."""

    placa: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Placa única del vehículo",
        examples=["ABC123"],
    )
    modelo: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Marca o modelo del vehículo",
        examples=["Renault Duster 2023"],
    )
    id_conductor: int = Field(
        ...,
        ge=1,
        description="ID del conductor asignado (FK)",
        examples=[1],
    )


class VehiculoCreate(VehiculoBase):
    """Esquema para creación de Vehiculo."""

    pass


class VehiculoUpdate(BaseModel):
    """
    Esquema para actualización de Vehiculo (soporta PATCH parcial y PUT total).
    Rechaza valores 'null' explícitos para proteger columnas NOT NULL en base de datos.
    """

    placa: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10,
        description="Placa única del vehículo",
    )
    modelo: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Marca o modelo del vehículo",
    )
    id_conductor: Optional[int] = Field(
        None,
        ge=1,
        description="ID del conductor asignado (FK)",
    )

    @field_validator("placa", "modelo", "id_conductor", mode="before")
    @classmethod
    def reject_null(cls, value: Any, info: ValidationInfo) -> Any:
        if value is None:
            raise ValueError(f"El campo '{info.field_name}' no puede ser nulo.")
        return value


class VehiculoRead(VehiculoBase):
    """Esquema de respuesta para Vehiculo."""

    id_vehiculo: int = Field(..., description="Identificador único del vehículo")

    model_config = ConfigDict(from_attributes=True)
