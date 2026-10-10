from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.vehiculo import Vehiculo


class Viaje(Base):
    """Modelo ORM para la tabla viajes."""

    __tablename__ = "viajes"

    id_viaje: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    destino: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    id_vehiculo: Mapped[int] = mapped_column(
        ForeignKey(
            "vehiculos.id_vehiculo",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    vehiculo: Mapped["Vehiculo"] = relationship(
        "Vehiculo",
        back_populates="viajes",
    )

    def __repr__(self) -> str:
        return (
            f"<Viaje(id={self.id_viaje}, destino={self.destino!r}, "
            f"fecha={self.fecha})>"
        )
