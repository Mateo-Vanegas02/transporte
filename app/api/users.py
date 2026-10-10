from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_user_service
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import (
    EmailAlreadyExistsException,
    UserNotFoundException,
    UserService,
)

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Retorna la lista de usuarios registrados con soporte para paginación.",
)
def list_users(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(
        100, ge=1, le=1000, description="Número máximo de registros a retornar"
    ),
    service: UserService = Depends(get_user_service),
) -> Sequence[UserRead]:
    return service.list_users(skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Retorna un usuario específico por su ID. Devuelve 404 si no existe.",
)
def get_user_by_id(
    id: int,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        return service.get_user_by_id(user_id=id)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
    description=(
        "Crea un usuario. Devuelve 409 Conflict si el email ya se encuentra "
        "registrado."
    ),
)
def create_user(
    user_in: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        return service.create_user(user_in=user_in)
    except EmailAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put(
    "/{id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
    description=(
        "Actualiza campos de un usuario existente por su ID. "
        "Devuelve 404 si no existe o 409 si el nuevo email ya está en uso."
    ),
)
def update_user(
    id: int,
    user_in: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    try:
        return service.update_user(user_id=id, user_in=user_in)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EmailAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario por su ID. Devuelve 404 si no existe.",
)
def delete_user(
    id: int,
    service: UserService = Depends(get_user_service),
) -> None:
    try:
        service.delete_user(user_id=id)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
