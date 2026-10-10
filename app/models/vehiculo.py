from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.conductor import Conductor
    from app.models.viaje import Viaje


class Vehiculo(Base):
    """Modelo ORM para la tabla vehiculos."""

    __tablename__ = "vehiculos"

    id_vehiculo: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    placa: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        index=True,
        nullable=False,
    )
    modelo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    id_conductor: Mapped[int] = mapped_column(
        ForeignKey(
            "conductores.id_conductor",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    conductor: Mapped["Conductor"] = relationship(
        "Conductor",
        back_populates="vehiculos",
    )
    viajes: Mapped[List["Viaje"]] = relationship(
        "Viaje",
        back_populates="vehiculo",
    )

    def __repr__(self) -> str:
        return (
            f"<Vehiculo(id={self.id_vehiculo}, placa={self.placa!r}, "
            f"modelo={self.modelo!r})>"
        )
