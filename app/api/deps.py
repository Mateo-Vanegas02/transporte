from collections.abc import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def get_db() -> Generator[Session, None, None]:
    """
    Generador de sesión de base de datos por petición HTTP.
    Garantiza que la sesión se cierre al finalizar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Inyección de dependencias para UserService.
    Instancia el UserRepository con la sesión de BD activa
    y lo inyecta en el servicio de usuarios.
    """
    repository = UserRepository(db)
    return UserService(repository)
