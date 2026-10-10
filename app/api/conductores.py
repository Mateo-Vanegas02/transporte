from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_conductor_service
from app.core.exceptions import (
    ConductorHasVehiculosException,
    ConductorNotFoundException,
    LicenciaAlreadyExistsException,
)
from app.schemas.conductor import (
    ConductorCreate,
    ConductorRead,
    ConductorUpdate,
)
from app.schemas.vehiculo import VehiculoRead
from app.services.conductor_service import ConductorService

router = APIRouter(prefix="/conductores", tags=["Conductores"])


@router.get(
    "",
    response_model=list[ConductorRead],
    status_code=status.HTTP_200_OK,
    summary="Listar conductores",
)
def list_conductores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: ConductorService = Depends(get_conductor_service),
) -> Sequence[ConductorRead]:
    return service.list_conductores(skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=ConductorRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener conductor por ID",
)
def get_conductor_by_id(
    id: int,
    service: ConductorService = Depends(get_conductor_service),
) -> ConductorRead:
    try:
        return service.get_by_id(id)
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{id}/vehiculos",
    response_model=list[VehiculoRead],
    status_code=status.HTTP_200_OK,
    summary="Listar vehículos asignados a un conductor",
)
def get_vehiculos_de_conductor(
    id: int,
    service: ConductorService = Depends(get_conductor_service),
) -> Sequence[VehiculoRead]:
    try:
        return service.get_vehiculos_by_conductor(id)
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ConductorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear conductor",
)
def create_conductor(
    conductor_in: ConductorCreate,
    service: ConductorService = Depends(get_conductor_service),
) -> ConductorRead:
    try:
        return service.create_conductor(conductor_in)
    except LicenciaAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put(
    "/{id}",
    response_model=ConductorRead,
    status_code=status.HTTP_200_OK,
    summary="Reemplazar/actualizar conductor",
)
def update_conductor_put(
    id: int,
    conductor_in: ConductorUpdate,
    service: ConductorService = Depends(get_conductor_service),
) -> ConductorRead:
    try:
        return service.update_conductor(id, conductor_in)
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except LicenciaAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{id}",
    response_model=ConductorRead,
    status_code=status.HTTP_200_OK,
    summary="Actualización parcial de conductor",
)
def update_conductor_patch(
    id: int,
    conductor_in: ConductorUpdate,
    service: ConductorService = Depends(get_conductor_service),
) -> ConductorRead:
    try:
        return service.update_conductor(id, conductor_in)
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except LicenciaAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar conductor",
)
def delete_conductor(
    id: int,
    service: ConductorService = Depends(get_conductor_service),
) -> None:
    try:
        service.delete_conductor(id)
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ConductorHasVehiculosException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
