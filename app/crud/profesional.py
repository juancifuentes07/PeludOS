from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.profesional import Profesional
from app.schemas.profesional import ProfesionalCreate, ProfesionalUpdate


def get_profesional_by_id(db: Session, id_profesional: int) -> Optional[Profesional]:
    """Busca un profesional por su ID, sin filtrar por estado activo."""
    return db.query(Profesional).filter(Profesional.id_profesional == id_profesional).first()


def get_profesionales_by_veterinaria(db: Session, id_veterinaria: int) -> List[Profesional]:
    """Lista los profesionales activos de una veterinaria."""
    return (
        db.query(Profesional)
        .filter(Profesional.id_veterinaria == id_veterinaria, Profesional.activo.is_(True))
        .all()
    )


def create_profesional(db: Session, profesional_data: ProfesionalCreate, id_veterinaria: int) -> Profesional:
    """Crea un nuevo profesional asociado a una veterinaria."""
    nuevo_profesional = Profesional(**profesional_data.model_dump(), id_veterinaria=id_veterinaria)
    db.add(nuevo_profesional)
    db.commit()
    db.refresh(nuevo_profesional)
    return nuevo_profesional


def update_profesional(db: Session, profesional: Profesional, profesional_data: ProfesionalUpdate) -> Profesional:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = profesional_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(profesional, campo, valor)
    db.commit()
    db.refresh(profesional)
    return profesional


def desactivar_profesional(db: Session, profesional: Profesional) -> Profesional:
    """Soft delete: marca al profesional como inactivo en vez de borrarlo físicamente."""
    profesional.activo = False
    db.commit()
    db.refresh(profesional)
    return profesional