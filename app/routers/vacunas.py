from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.vacuna import VacunaCreate, VacunaResponse, VacunaUpdate
from app.crud.mascota import get_mascota_by_id
from app.crud.vacuna import (
    get_vacuna_by_id,
    get_vacunas_by_mascota,
    create_vacuna,
    update_vacuna,
    eliminar_vacuna,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/mascotas/{id_mascota}/vacunas", tags=["Vacunas"])


def _get_mascota_propia(db: Session, id_mascota: int, usuario_actual: Usuario):
    mascota = get_mascota_by_id(db, id_mascota)
    if mascota is None or mascota.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
    return mascota


def _get_vacuna_propia(db: Session, id_mascota: int, id_vacuna: int, usuario_actual: Usuario):
    _get_mascota_propia(db, id_mascota, usuario_actual)
    vacuna = get_vacuna_by_id(db, id_vacuna)
    if vacuna is None or vacuna.id_mascota != id_mascota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacuna no encontrada")
    return vacuna


@router.get("/", response_model=List[VacunaResponse])
def read_vacunas(
    id_mascota: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista las vacunas registradas de una mascota del usuario autenticado."""
    _get_mascota_propia(db, id_mascota, usuario_actual)
    return get_vacunas_by_mascota(db, id_mascota)


@router.post("/", response_model=VacunaResponse, status_code=status.HTTP_201_CREATED)
def create_new_vacuna(
    id_mascota: int,
    vacuna_data: VacunaCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra una nueva vacuna aplicada a una mascota del usuario autenticado."""
    _get_mascota_propia(db, id_mascota, usuario_actual)
    if vacuna_data.id_mascota != id_mascota:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id_mascota del body no coincide con el de la URL",
        )
    return create_vacuna(db, vacuna_data)


@router.get("/{id_vacuna}", response_model=VacunaResponse)
def read_vacuna(
    id_mascota: int,
    id_vacuna: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el detalle de una vacuna."""
    return _get_vacuna_propia(db, id_mascota, id_vacuna, usuario_actual)


@router.patch("/{id_vacuna}", response_model=VacunaResponse)
def update_existing_vacuna(
    id_mascota: int,
    id_vacuna: int,
    vacuna_data: VacunaUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza una vacuna (actualización parcial)."""
    vacuna = _get_vacuna_propia(db, id_mascota, id_vacuna, usuario_actual)
    return update_vacuna(db, vacuna, vacuna_data)


@router.delete("/{id_vacuna}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vacuna(
    id_mascota: int,
    id_vacuna: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Elimina físicamente una vacuna (esta tabla no tiene campo 'activo').
    Devuelve 204 sin body, a diferencia de los demás DELETE del proyecto
    que devuelven el registro desactivado.
    """
    vacuna = _get_vacuna_propia(db, id_mascota, id_vacuna, usuario_actual)
    eliminar_vacuna(db, vacuna)