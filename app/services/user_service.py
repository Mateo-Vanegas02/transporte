from typing import Sequence

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserServiceException(Exception):
    """Excepción base para errores en la capa de servicio de usuarios."""

    pass


class UserNotFoundException(UserServiceException):
    """Se lanza cuando un usuario requerido no existe en el sistema."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"Usuario con id {user_id} no fue encontrado.")


class EmailAlreadyExistsException(UserServiceException):
    """Se lanza al intentar registrar o actualizar con un email ya en uso."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"El email '{email}' ya se encuentra registrado.")


# Alias semánticos requeridos por especificación
UserNotFound = UserNotFoundException
EmailAlreadyExists = EmailAlreadyExistsException


class UserService:
    """
    Capa de servicio que orquesta la lógica de negocio para usuarios.
    Aplica reglas de negocio (ej. unicidad de email, existencia) y lanza
    excepciones de dominio desacopladas del protocolo HTTP.
    """

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def get_user_by_id(self, user_id: int) -> User:
        """Obtiene un usuario por ID o lanza UserNotFoundException si no existe."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Retorna una lista paginada de usuarios."""
        return self.repository.get_all(skip=skip, limit=limit)

    def create_user(self, user_in: UserCreate) -> User:
        """
        Crea un nuevo usuario validando que el email no esté duplicado.
        Lanza EmailAlreadyExistsException si ya existe un usuario con dicho email.
        """
        existing_user = self.repository.get_by_email(str(user_in.email))
        if existing_user:
            raise EmailAlreadyExistsException(str(user_in.email))

        return self.repository.create(user_in)

    def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """
        Actualiza un usuario existente.
        Valida existencia y que el nuevo email (si cambió) no esté
        tomado por otro usuario.
        """
        user = self.get_user_by_id(user_id)

        # Si se envía un email y es diferente al actual, verificar unicidad
        if user_in.email is not None and str(user_in.email) != user.email:
            existing_email_user = self.repository.get_by_email(str(user_in.email))
            if existing_email_user and existing_email_user.id != user_id:
                raise EmailAlreadyExistsException(str(user_in.email))

        return self.repository.update(user, user_in)

    def delete_user(self, user_id: int) -> None:
        """
        Elimina un usuario por su ID.
        Valida que el usuario exista antes de eliminarlo.
        """
        user = self.get_user_by_id(user_id)
        self.repository.delete(user)
