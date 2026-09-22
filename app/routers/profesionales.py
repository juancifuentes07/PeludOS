from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.profesional import ProfesionalCreate, ProfesionalResponse, ProfesionalUpdate
from app.crud.veterinaria import get_veterinaria_by_id
from app.crud.profesional import (
    get_profesional_by_id,
    get_profesionales_by_veterinaria,
    create_profesional,
    update_profesional,
    desactivar_profesional,
)
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/veterinarias/{id_veterinaria}/profesionales", tags=["Profesionales"])


def _get_veterinaria_o_404(db: Session, id_veterinaria: int):
    veterinaria = get_veterinaria_by_id(db, id_veterinaria)
    if veterinaria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinaria no encontrada")
    return veterinaria


@router.get("/", response_model=List[ProfesionalResponse])
def read_profesionales(
    id_veterinaria: int,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Lista los profesionales activos de una veterinaria."""
    _get_veterinaria_o_404(db, id_veterinaria)
    return get_profesionales_by_veterinaria(db, id_veterinaria)


@router.post("/", response_model=ProfesionalResponse, status_code=status.HTTP_201_CREATED)
def create_new_profesional(
    id_veterinaria: int,
    profesional_data: ProfesionalCreate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Registra un nuevo profesional en una veterinaria. Requiere rol admin."""
    require_admin(usuario_actual)
    _get_veterinaria_o_404(db, id_veterinaria)
    return create_profesional(db, profesional_data, id_veterinaria)


@router.patch("/{id_profesional}", response_model=ProfesionalResponse)
def update_existing_profesional(
    id_veterinaria: int,
    id_profesional: int,
    profesional_data: ProfesionalUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza un profesional (actualización parcial). Requiere rol admin."""
    
    profesional = get_profesional_by_id(db, id_profesional)
    if profesional is None or profesional.id_veterinaria != id_veterinaria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")
    return update_profesional(db, profesional, profesional_data)


@router.delete("/{id_profesional}", response_model=ProfesionalResponse)
def deactivate_profesional(
    id_veterinaria: int,
    id_profesional: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desactiva (soft delete) un profesional. Requiere rol admin."""
    
    profesional = get_profesional_by_id(db, id_profesional)
    if profesional is None or profesional.id_veterinaria != id_veterinaria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")
    return desactivar_profesional(db, profesional)