from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Esquema base que contiene los atributos compartidos de usuario."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre completo del usuario",
        examples=["Juan Pérez"],
    )
    email: EmailStr = Field(
        ...,
        max_length=150,
        description="Correo electrónico único del usuario",
        examples=["juan.perez@example.com"],
    )


class UserCreate(UserBase):
    """Esquema para la creación de un nuevo usuario."""

    pass


class UserUpdate(BaseModel):
    """Esquema para la actualización parcial o total de un usuario."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Nombre completo del usuario",
        examples=["Juan Carlos Pérez"],
    )
    email: Optional[EmailStr] = Field(
        None,
        max_length=150,
        description="Correo electrónico del usuario",
        examples=["juancarlos@example.com"],
    )


class UserRead(UserBase):
    """Esquema de lectura para respuestas de la API."""

    id: int = Field(..., description="Identificador único del usuario")

    model_config = ConfigDict(from_attributes=True)
