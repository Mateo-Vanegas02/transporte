from datetime import date
from typing import Optional, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_viaje_service
from app.core.exceptions import (
    VehiculoNotFoundException,
    ViajeNotFoundException,
)
from app.schemas.viaje import (
    ViajeCreate,
    ViajeDetalleRead,
    ViajeRead,
    ViajeUpdate,
)
from app.services.viaje_service import ViajeService

router = APIRouter(prefix="/viajes", tags=["Viajes"])


@router.get(
    "",
    response_model=list[ViajeRead],
    status_code=status.HTTP_200_OK,
    summary="Listar viajes con filtros",
    description=(
        "Permite consultar viajes filtrando por rango de fechas, " "destino y vehículo."
    ),
)
def list_viajes(
    fecha_desde: Optional[date] = Query(None, description="Fecha mínima (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha máxima (YYYY-MM-DD)"),
    destino: Optional[str] = Query(None, description="Búsqueda por texto en destino"),
    id_vehiculo: Optional[int] = Query(None, description="Filtrar por ID de vehículo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: ViajeService = Depends(get_viaje_service),
) -> Sequence[ViajeRead]:
    return service.list_viajes(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        destino=destino,
        id_vehiculo=id_vehiculo,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/detalle",
    response_model=list[ViajeDetalleRead],
    status_code=status.HTTP_200_OK,
    summary="Reporte consolidado de viajes (JOIN 3 tablas)",
    description=(
        "Retorna información combinada de viaje, vehículo y conductor "
        "optimizada con joinedload para evitar consultas N+1."
    ),
)
def get_viajes_detalle(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: ViajeService = Depends(get_viaje_service),
) -> list[ViajeDetalleRead]:
    return service.list_detalles(skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=ViajeRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener viaje por ID",
)
def get_viaje_by_id(
    id: int,
    service: ViajeService = Depends(get_viaje_service),
) -> ViajeRead:
    try:
        return service.get_by_id(id)
    except ViajeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ViajeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear viaje",
)
def create_viaje(
    viaje_in: ViajeCreate,
    service: ViajeService = Depends(get_viaje_service),
) -> ViajeRead:
    try:
        return service.create_viaje(viaje_in)
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{id}",
    response_model=ViajeRead,
    status_code=status.HTTP_200_OK,
    summary="Reemplazar/actualizar viaje",
)
def update_viaje_put(
    id: int,
    viaje_in: ViajeUpdate,
    service: ViajeService = Depends(get_viaje_service),
) -> ViajeRead:
    try:
        return service.update_viaje(id, viaje_in)
    except ViajeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{id}",
    response_model=ViajeRead,
    status_code=status.HTTP_200_OK,
    summary="Actualización parcial de viaje",
)
def update_viaje_patch(
    id: int,
    viaje_in: ViajeUpdate,
    service: ViajeService = Depends(get_viaje_service),
) -> ViajeRead:
    try:
        return service.update_viaje(id, viaje_in)
    except ViajeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except VehiculoNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar viaje",
)
def delete_viaje(
    id: int,
    service: ViajeService = Depends(get_viaje_service),
) -> None:
    try:
        service.delete_viaje(id)
    except ViajeNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
