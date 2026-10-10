from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class ConductorBase(BaseModel):
    """Atributos base para la entidad Conductor."""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre completo del conductor",
        examples=["Mateo Vanegas"],
    )
    licencia: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Número de licencia de conducción único",
        examples=["LIC-1001"],
    )
    telefono: str = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Número telefónico de contacto",
        examples=["3001234567"],
    )


class ConductorCreate(ConductorBase):
    """Esquema para creación de Conductor."""

    pass


class ConductorUpdate(BaseModel):
    """
    Esquema para actualización de Conductor (soporta PATCH parcial y PUT total).
    Rechaza valores 'null' explícitos para proteger columnas NOT NULL en base de datos.
    """

    nombre: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Nombre completo del conductor",
    )
    licencia: Optional[str] = Field(
        None,
        min_length=1,
        max_length=20,
        description="Número de licencia de conducción único",
    )
    telefono: Optional[str] = Field(
        None,
        min_length=1,
        max_length=15,
        description="Número telefónico de contacto",
    )

    @field_validator("nombre", "licencia", "telefono", mode="before")
    @classmethod
    def reject_null(cls, value: Any, info: ValidationInfo) -> Any:
        if value is None:
            raise ValueError(f"El campo '{info.field_name}' no puede ser nulo.")
        return value


class ConductorRead(ConductorBase):
    """Esquema de respuesta para Conductor."""

    id_conductor: int = Field(..., description="Identificador único del conductor")

    model_config = ConfigDict(from_attributes=True)
