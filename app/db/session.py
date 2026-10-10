from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM de SQLAlchemy."""

    pass


# Engine de SQLAlchemy configurado con pool_pre_ping=True
# Esto valida que la conexión esté viva antes de usarla,
# evitando errores por timeouts o reconexiones de MySQL.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Fábrica de sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
