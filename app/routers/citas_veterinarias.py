from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.cita_veterinaria import CitaVeterinaria
from app.schemas.cita_veterinaria import (
    CitaVeterinariaCreate,
    CitaVeterinariaResponse,
    CitaVeterinariaUpdate,
)
from app.crud.mascota import get_mascota_by_id
from app.crud.veterinaria import get_veterinaria_by_id
from app.crud.profesional import get_profesional_by_id
from app.crud.cita_veterinaria import (
    get_cita_by_id,
    get_citas_by_usuario,
    create_cita,
    update_cita,
    cancelar_cita,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/citas", tags=["Citas Veterinarias"])


def _get_cita_propia(db: Session, id_cita: int, usuario_actual: Usuario) -> CitaVeterinaria:
    """
    Obtiene una cita validando que la mascota asociada pertenezca al usuario autenticado,
    o que el usuario sea admin. Responde 404 si no existe o no le pertenece, para no
    revelar la existencia de citas ajenas.
    """
    cita = get_cita_by_id(db, id_cita)
    if cita is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada")

    if usuario_actual.rol != "admin" and cita.mascota.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada")

    return cita


@router.get("/", response_model=List[CitaVeterinariaResponse])
def read_citas(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista las citas de las mascotas del usuario autenticado.
    """
    return get_citas_by_usuario(db, usuario_actual.id_usuario)


@router.post("/", response_model=CitaVeterinariaResponse, status_code=status.HTTP_201_CREATED)
def create_new_cita(
    cita_data: CitaVeterinariaCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Agenda una nueva cita veterinaria para una mascota del usuario autenticado.
    Valida que la mascota sea del usuario, que la veterinaria exista y esté activa,
    y que el profesional pertenezca a esa veterinaria.
    """
    mascota = get_mascota_by_id(db, cita_data.id_mascota)
    if mascota is None or mascota.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")

    veterinaria = get_veterinaria_by_id(db, cita_data.id_veterinaria)
    if veterinaria is None or not veterinaria.activo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinaria no encontrada")

    profesional = get_profesional_by_id(db, cita_data.id_profesional)
    if profesional is None or profesional.id_veterinaria != cita_data.id_veterinaria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El profesional no pertenece a la veterinaria indicada",
        )

    return create_cita(db, cita_data)


@router.get("/{id_cita}", response_model=CitaVeterinariaResponse)
def read_cita(
    id_cita: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Devuelve el detalle de una cita del usuario autenticado (o de cualquiera, si es admin).
    """
    return _get_cita_propia(db, id_cita, usuario_actual)


@router.patch("/{id_cita}", response_model=CitaVeterinariaResponse)
def update_existing_cita(
    id_cita: int,
    cita_data: CitaVeterinariaUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza una cita (actualización parcial).
    AJUSTAR: por ahora el dueño puede modificar cualquier campo, incluido 'estado'.
    Cuando el flujo de la veterinaria esté más maduro, considera restringir
    el cambio de 'estado' a un rol específico (veterinaria/admin) y dejar
    que el dueño solo edite motivo/fecha/notas mientras la cita siga 'programada'.
    """
    cita = _get_cita_propia(db, id_cita, usuario_actual)
    return update_cita(db, cita, cita_data)


@router.delete("/{id_cita}", response_model=CitaVeterinariaResponse)
def cancel_cita(
    id_cita: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancela una cita (cambia su estado a 'cancelada'). No hay borrado físico.
    """
    cita = _get_cita_propia(db, id_cita, usuario_actual)
    return cancelar_cita(db, cita)