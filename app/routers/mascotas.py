from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.mascota import Mascota
from app.schemas.mascota import MascotaCreate, MascotaResponse, MascotaUpdate
from app.crud.mascota import (
    get_mascota_by_id,
    get_mascota_by_chip,
    get_mascotas_by_usuario,
    create_mascota,
    update_mascota,
    desactivar_mascota,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/mascotas", tags=["Mascotas"])


def _get_mascota_propia(db: Session, id_mascota: int, usuario_actual: Usuario) -> Mascota:
    """
    Obtiene una mascota validando que pertenezca al usuario autenticado.
    Responde 404 tanto si no existe como si es de otro dueño, para no
    revelar la existencia de mascotas ajenas.
    """
    mascota = get_mascota_by_id(db, id_mascota)
    if mascota is None or mascota.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada",
        )
    return mascota


@router.get("/", response_model=List[MascotaResponse])
def read_mascotas(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista las mascotas activas del usuario autenticado.
    """
    return get_mascotas_by_usuario(db, usuario_actual.id_usuario)


@router.post("/", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
def create_new_mascota(
    mascota_data: MascotaCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registra una nueva mascota a nombre del usuario autenticado.
    Valida que el número de chip no esté registrado previamente.
    """
    if mascota_data.numero_chip and get_mascota_by_chip(db, mascota_data.numero_chip):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una mascota registrada con ese número de chip",
        )
    return create_mascota(db, mascota_data, usuario_actual.id_usuario)


@router.get("/{id_mascota}", response_model=MascotaResponse)
def read_mascota(
    id_mascota: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Devuelve el detalle de una mascota del usuario autenticado.
    """
    return _get_mascota_propia(db, id_mascota, usuario_actual)


@router.patch("/{id_mascota}", response_model=MascotaResponse)
def update_existing_mascota(
    id_mascota: int,
    mascota_data: MascotaUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza los datos de una mascota del usuario autenticado
    (actualización parcial).
    """
    mascota = _get_mascota_propia(db, id_mascota, usuario_actual)

    if mascota_data.numero_chip and mascota_data.numero_chip != mascota.numero_chip:
        if get_mascota_by_chip(db, mascota_data.numero_chip):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una mascota registrada con ese número de chip",
            )

    return update_mascota(db, mascota, mascota_data)


@router.delete("/{id_mascota}", response_model=MascotaResponse)
def deactivate_mascota(
    id_mascota: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desactiva (soft delete) una mascota del usuario autenticado.
    No borra el registro físicamente.
    """
    mascota = _get_mascota_propia(db, id_mascota, usuario_actual)
    return desactivar_mascota(db, mascota)