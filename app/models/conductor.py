from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.vehiculo import Vehiculo


class Conductor(Base):
    """Modelo ORM para la tabla conductores."""

    __tablename__ = "conductores"

    id_conductor: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    licencia: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )
    telefono: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    vehiculos: Mapped[List["Vehiculo"]] = relationship(
        "Vehiculo",
        back_populates="conductor",
    )

    def __repr__(self) -> str:
        return (
            f"<Conductor(id={self.id_conductor}, nombre={self.nombre!r}, "
            f"licencia={self.licencia!r})>"
        )
