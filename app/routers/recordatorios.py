from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.recordatorio import Recordatorio
from app.schemas.recordatorio import RecordatorioCreate, RecordatorioResponse, RecordatorioUpdate
from app.crud.mascota import get_mascota_by_id
from app.crud.recordatorio import (
    get_recordatorio_by_id,
    get_recordatorios_by_mascota,
    create_recordatorio,
    update_recordatorio,
    desactivar_recordatorio,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/mascotas/{id_mascota}/recordatorios", tags=["Recordatorios"])


def _get_mascota_propia(db: Session, id_mascota: int, usuario_actual: Usuario):
    mascota = get_mascota_by_id(db, id_mascota)
    if mascota is None or mascota.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
    return mascota


def _get_recordatorio_propio(db: Session, id_mascota: int, id_recordatorio: int, usuario_actual: Usuario) -> Recordatorio:
    _get_mascota_propia(db, id_mascota, usuario_actual)
    recordatorio = get_recordatorio_by_id(db, id_recordatorio)
    if recordatorio is None or recordatorio.id_mascota != id_mascota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recordatorio no encontrado")
    return recordatorio


@router.get("/", response_model=List[RecordatorioResponse])
def read_recordatorios(
    id_mascota: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los recordatorios activos de una mascota del usuario autenticado."""
    _get_mascota_propia(db, id_mascota, usuario_actual)
    return get_recordatorios_by_mascota(db, id_mascota)


@router.post("/", response_model=RecordatorioResponse, status_code=status.HTTP_201_CREATED)
def create_new_recordatorio(
    id_mascota: int,
    recordatorio_data: RecordatorioCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuevo recordatorio para una mascota del usuario autenticado."""
    _get_mascota_propia(db, id_mascota, usuario_actual)
    if recordatorio_data.id_mascota != id_mascota:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id_mascota del body no coincide con el de la URL",
        )
    return create_recordatorio(db, recordatorio_data)


@router.get("/{id_recordatorio}", response_model=RecordatorioResponse)
def read_recordatorio(
    id_mascota: int,
    id_recordatorio: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el detalle de un recordatorio."""
    return _get_recordatorio_propio(db, id_mascota, id_recordatorio, usuario_actual)


@router.patch("/{id_recordatorio}", response_model=RecordatorioResponse)
def update_existing_recordatorio(
    id_mascota: int,
    id_recordatorio: int,
    recordatorio_data: RecordatorioUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un recordatorio (actualización parcial)."""
    recordatorio = _get_recordatorio_propio(db, id_mascota, id_recordatorio, usuario_actual)
    return update_recordatorio(db, recordatorio, recordatorio_data)


@router.delete("/{id_recordatorio}", response_model=RecordatorioResponse)
def deactivate_recordatorio(
    id_mascota: int,
    id_recordatorio: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desactiva (soft delete) un recordatorio."""
    recordatorio = _get_recordatorio_propio(db, id_mascota, id_recordatorio, usuario_actual)
    return desactivar_recordatorio(db, recordatorio)