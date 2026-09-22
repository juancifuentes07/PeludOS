from typing import Optional

from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password


def get_usuario_by_id(db: Session, id_usuario: int) -> Optional[Usuario]:
    """Busca un usuario por su ID."""
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()


def get_usuario_by_correo(db: Session, correo_electronico: str) -> Optional[Usuario]:
    """Busca un usuario por su correo electrónico (usado en login y validación de duplicados)."""
    return db.query(Usuario).filter(Usuario.correo_electronico == correo_electronico).first()


def create_usuario(db: Session, usuario_data: UsuarioCreate) -> Usuario:
    """Crea un nuevo usuario, hasheando la contraseña antes de guardarla."""
    nuevo_usuario = Usuario(
        nombre_completo=usuario_data.nombre_completo,
        correo_electronico=usuario_data.correo_electronico,
        contrasena_hash=hash_password(usuario_data.contrasena),
        telefono=usuario_data.telefono,
        direccion=usuario_data.direccion,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def update_usuario(db: Session, usuario: Usuario, usuario_data: UsuarioUpdate) -> Usuario:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = usuario_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def desactivar_usuario(db: Session, usuario: Usuario) -> Usuario:
    """Soft delete: marca el usuario como inactivo en vez de borrarlo físicamente."""
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario