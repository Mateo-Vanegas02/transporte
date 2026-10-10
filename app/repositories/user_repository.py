from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    """
    Repositorio para la entidad User.
    Responsabilidad exclusiva: operaciones directas de persistencia
    y consulta con SQLAlchemy.
    No contiene lógica de negocio ni validaciones de dominio.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su identificador primario."""
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su dirección de email."""
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Obtiene una lista paginada de usuarios."""
        stmt = select(User).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, user_in: UserCreate) -> User:
        """Crea y persiste un nuevo usuario en la base de datos."""
        user = User(
            name=user_in.name,
            email=str(user_in.email),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, user_in: UserUpdate) -> User:
        """Actualiza los campos provistos de un usuario existente."""
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "email" and value is not None:
                value = str(value)
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Elimina un usuario de la base de datos."""
        self.db.delete(user)
        self.db.commit()
