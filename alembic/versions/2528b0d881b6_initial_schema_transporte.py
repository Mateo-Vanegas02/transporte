"""initial_schema_transporte

Revision ID: 2528b0d881b6
Revises:
Create Date: 2026-10-10 15:10:31.961391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2528b0d881b6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea las tablas del dominio transporte si no existen."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if "conductores" not in existing_tables:
        op.create_table(
            "conductores",
            sa.Column(
                "id_conductor",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column("nombre", sa.String(length=100), nullable=False),
            sa.Column("licencia", sa.String(length=20), nullable=False),
            sa.Column("telefono", sa.String(length=15), nullable=False),
            sa.PrimaryKeyConstraint("id_conductor"),
            sa.UniqueConstraint("licencia"),
        )
        op.create_index(
            op.f("ix_conductores_id_conductor"),
            "conductores",
            ["id_conductor"],
            unique=False,
        )
        op.create_index(
            op.f("ix_conductores_licencia"),
            "conductores",
            ["licencia"],
            unique=True,
        )

    if "vehiculos" not in existing_tables:
        op.create_table(
            "vehiculos",
            sa.Column(
                "id_vehiculo",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column("placa", sa.String(length=10), nullable=False),
            sa.Column("modelo", sa.String(length=50), nullable=False),
            sa.Column("id_conductor", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["id_conductor"],
                ["conductores.id_conductor"],
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            sa.PrimaryKeyConstraint("id_vehiculo"),
            sa.UniqueConstraint("placa"),
        )
        op.create_index(
            op.f("ix_vehiculos_id_vehiculo"),
            "vehiculos",
            ["id_vehiculo"],
            unique=False,
        )
        op.create_index(
            op.f("ix_vehiculos_id_conductor"),
            "vehiculos",
            ["id_conductor"],
            unique=False,
        )
        op.create_index(
            op.f("ix_vehiculos_placa"),
            "vehiculos",
            ["placa"],
            unique=True,
        )

    if "viajes" not in existing_tables:
        op.create_table(
            "viajes",
            sa.Column(
                "id_viaje",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column("destino", sa.String(length=100), nullable=False),
            sa.Column("fecha", sa.Date(), nullable=False),
            sa.Column("id_vehiculo", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(
                ["id_vehiculo"],
                ["vehiculos.id_vehiculo"],
                onupdate="CASCADE",
                ondelete="RESTRICT",
            ),
            sa.PrimaryKeyConstraint("id_viaje"),
        )
        op.create_index(
            op.f("ix_viajes_id_viaje"),
            "viajes",
            ["id_viaje"],
            unique=False,
        )
        op.create_index(
            op.f("ix_viajes_id_vehiculo"),
            "viajes",
            ["id_vehiculo"],
            unique=False,
        )


def downgrade() -> None:
    """Elimina las tablas en orden inverso respetando restricciones de clave foránea."""
    op.drop_table("viajes")
    op.drop_table("vehiculos")
    op.drop_table("conductores")
