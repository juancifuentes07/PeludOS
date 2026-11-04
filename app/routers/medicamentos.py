from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.medicamento import MedicamentoCreate, MedicamentoResponse, MedicamentoUpdate
from app.crud.mascota import get_mascota_by_id
from app.crud.medicamento import (
    get_medicamento_by_id,
    get_medicamentos_by_mascota,
    create_medicamento,
    update_medicamento,
    desactivar_medicamento,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/mascotas/{id_mascota}/medicamentos", tags=["Medicamentos"])


def _get_mascota_propia(db: Session, id_mascota: int, usuario_actual: Usuario):
    mascota = get_mascota_by_id(db, id_mascota)
    if mascota is None or mascota.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
    return mascota


def _get_medicamento_propio(db: Session, id_mascota: int, id_medicamento: int, usuario_actual: Usuario):
    _get_mascota_propia(db, id_mascota, usuario_actual)
    medicamento = get_medicamento_by_id(db, id_medicamento)
    if medicamento is None or medicamento.id_mascota != id_mascota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicamento no encontrado")
    return medicamento


@router.get("/", response_model=List[MedicamentoResponse])
def read_medicamentos(
    id_mascota: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los medicamentos activos de una mascota del usuario autenticado."""
    _get_mascota_propia(db, id_mascota, usuario_actual)
    return get_medicamentos_by_mascota(db, id_mascota)


@router.post("/", response_model=MedicamentoResponse, status_code=status.HTTP_201_CREATED)
def create_new_medicamento(
    id_mascota: int,
    medicamento_data: MedicamentoCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra un nuevo medicamento para una mascota del usuario autenticado."""
    _get_mascota_propia(db, id_mascota, usuario_actual)
    if medicamento_data.id_mascota != id_mascota:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id_mascota del body no coincide con el de la URL",
        )
    return create_medicamento(db, medicamento_data)


@router.get("/{id_medicamento}", response_model=MedicamentoResponse)
def read_medicamento(
    id_mascota: int,
    id_medicamento: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el detalle de un medicamento."""
    return _get_medicamento_propio(db, id_mascota, id_medicamento, usuario_actual)


@router.patch("/{id_medicamento}", response_model=MedicamentoResponse)
def update_existing_medicamento(
    id_mascota: int,
    id_medicamento: int,
    medicamento_data: MedicamentoUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un medicamento (actualización parcial)."""
    medicamento = _get_medicamento_propio(db, id_mascota, id_medicamento, usuario_actual)
    return update_medicamento(db, medicamento, medicamento_data)


@router.delete("/{id_medicamento}", response_model=MedicamentoResponse)
def deactivate_medicamento(
    id_mascota: int,
    id_medicamento: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desactiva (soft delete) un medicamento."""
    medicamento = _get_medicamento_propio(db, id_mascota, id_medicamento, usuario_actual)
    return desactivar_medicamento(db, medicamento)