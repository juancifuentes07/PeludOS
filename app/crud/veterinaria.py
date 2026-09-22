from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.veterinaria import Veterinaria
from app.schemas.veterinaria import VeterinariaCreate, VeterinariaUpdate


def get_veterinaria_by_id(db: Session, id_veterinaria: int) -> Optional[Veterinaria]:
    """Busca una veterinaria por su ID, sin filtrar por estado activo."""
    return db.query(Veterinaria).filter(Veterinaria.id_veterinaria == id_veterinaria).first()


def get_veterinarias(db: Session) -> List[Veterinaria]:
    """Lista todas las veterinarias activas."""
    return db.query(Veterinaria).filter(Veterinaria.activo.is_(True)).all()


def create_veterinaria(db: Session, veterinaria_data: VeterinariaCreate) -> Veterinaria:
    """Crea una nueva veterinaria."""
    nueva_veterinaria = Veterinaria(**veterinaria_data.model_dump())
    db.add(nueva_veterinaria)
    db.commit()
    db.refresh(nueva_veterinaria)
    return nueva_veterinaria


def update_veterinaria(db: Session, veterinaria: Veterinaria, veterinaria_data: VeterinariaUpdate) -> Veterinaria:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = veterinaria_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(veterinaria, campo, valor)
    db.commit()
    db.refresh(veterinaria)
    return veterinaria


def desactivar_veterinaria(db: Session, veterinaria: Veterinaria) -> Veterinaria:
    """Soft delete: marca la veterinaria como inactiva en vez de borrarla físicamente."""
    veterinaria.activo = False
    db.commit()
    db.refresh(veterinaria)
    return veterinaria