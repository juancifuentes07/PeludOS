from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioResponse, UsuarioUpdate
from app.crud.usuario import update_usuario, desactivar_usuario
from app.core.security import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioResponse)
def read_current_user(usuario_actual: Usuario = Depends(get_current_user)):
    """
    Devuelve la información del usuario autenticado (dueño del token).
    """
    return usuario_actual


@router.patch("/me", response_model=UsuarioResponse)
def update_current_user(
    usuario_data: UsuarioUpdate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza los datos del usuario autenticado (actualización parcial).
    """
    return update_usuario(db, usuario_actual, usuario_data)


@router.delete("/me", response_model=UsuarioResponse)
def deactivate_current_user(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desactiva (soft delete) al usuario autenticado. No borra el registro físicamente.
    """
    return desactivar_usuario(db, usuario_actual)