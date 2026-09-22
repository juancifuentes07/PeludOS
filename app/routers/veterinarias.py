from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.veterinaria import VeterinariaCreate, VeterinariaResponse, VeterinariaUpdate
from app.crud.veterinaria import (
    get_veterinaria_by_id,
    get_veterinarias,
    create_veterinaria,
    update_veterinaria,
    desactivar_veterinaria,
)
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/veterinarias", tags=["Veterinarias"])



@router.get("/", response_model=List[VeterinariaResponse])
def read_veterinarias(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista las veterinarias activas. Disponible para cualquier usuario autenticado.
    """
    return get_veterinarias(db)


@router.get("/{id_veterinaria}", response_model=VeterinariaResponse)
def read_veterinaria(
    id_veterinaria: int,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Devuelve el detalle de una veterinaria.
    """
    veterinaria = get_veterinaria_by_id(db, id_veterinaria)
    if veterinaria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinaria no encontrada")
    return veterinaria


@router.post("/", response_model=VeterinariaResponse, status_code=status.HTTP_201_CREATED)
def create_new_veterinaria(
    veterinaria_data: VeterinariaCreate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Registra una nueva veterinaria. Requiere rol admin.
    """
    
    return create_veterinaria(db, veterinaria_data)


@router.patch("/{id_veterinaria}", response_model=VeterinariaResponse)
def update_existing_veterinaria(
    id_veterinaria: int,
    veterinaria_data: VeterinariaUpdate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Actualiza una veterinaria (actualización parcial). Requiere rol admin.
    """
    
    veterinaria = get_veterinaria_by_id(db, id_veterinaria)
    if veterinaria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinaria no encontrada")
    return update_veterinaria(db, veterinaria, veterinaria_data)


@router.delete("/{id_veterinaria}", response_model=VeterinariaResponse)
def deactivate_veterinaria(
    id_veterinaria: int,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Desactiva (soft delete) una veterinaria. Requiere rol admin.
    """
    
    veterinaria = get_veterinaria_by_id(db, id_veterinaria)
    if veterinaria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinaria no encontrada")
    return desactivar_veterinaria(db, veterinaria)