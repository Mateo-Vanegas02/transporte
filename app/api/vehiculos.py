from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_vehiculo_service
from app.core.exceptions import (
    ConductorNotFoundException,
    PlacaAlreadyExistsException,
    VehiculoHasViajesException,
    VehiculoNotFoundException,
)
from app.schemas.vehiculo import (
    VehiculoCreate,
    VehiculoRead,
    VehiculoUpdate,
)
from app.schemas.viaje import ViajeRead
from app.services.vehiculo_service import VehiculoService

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


@router.get(
    "",
    response_model=list[VehiculoRead],
    status_code=status.HTTP_200_OK,
    summary="Listar vehículos",
)
def list_vehiculos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: VehiculoService = Depends(get_vehiculo_service),
) -> Sequence[VehiculoRead]:
    return service.list_vehiculos(skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=VehiculoRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener vehículo por ID",
)
def get_vehiculo_by_id(
    id: int,
    service: VehiculoService = Depends(get_vehiculo_service),
) -> VehiculoRead:
    try:
        return service.get_by_id(id)
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{id}/viajes",
    response_model=list[ViajeRead],
    status_code=status.HTTP_200_OK,
    summary="Listar viajes de un vehículo",
)
def get_viajes_de_vehiculo(
    id: int,
    service: VehiculoService = Depends(get_vehiculo_service),
) -> Sequence[ViajeRead]:
    try:
        return service.get_viajes_by_vehiculo(id)
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=VehiculoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear vehículo",
)
def create_vehiculo(
    vehiculo_in: VehiculoCreate,
    service: VehiculoService = Depends(get_vehiculo_service),
) -> VehiculoRead:
    try:
        return service.create_vehiculo(vehiculo_in)
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PlacaAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put(
    "/{id}",
    response_model=VehiculoRead,
    status_code=status.HTTP_200_OK,
    summary="Reemplazar/actualizar vehículo",
)
def update_vehiculo_put(
    id: int,
    vehiculo_in: VehiculoUpdate,
    service: VehiculoService = Depends(get_vehiculo_service),
) -> VehiculoRead:
    try:
        return service.update_vehiculo(id, vehiculo_in)
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PlacaAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{id}",
    response_model=VehiculoRead,
    status_code=status.HTTP_200_OK,
    summary="Actualización parcial de vehículo",
)
def update_vehiculo_patch(
    id: int,
    vehiculo_in: VehiculoUpdate,
    service: VehiculoService = Depends(get_vehiculo_service),
) -> VehiculoRead:
    try:
        return service.update_vehiculo(id, vehiculo_in)
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ConductorNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PlacaAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar vehículo",
)
def delete_vehiculo(
    id: int,
    service: VehiculoService = Depends(get_vehiculo_service),
) -> None:
    try:
        service.delete_vehiculo(id)
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except VehiculoHasViajesException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
