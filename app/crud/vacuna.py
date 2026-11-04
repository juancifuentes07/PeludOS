from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.vacuna import Vacuna
from app.schemas.vacuna import VacunaCreate, VacunaUpdate


def get_vacuna_by_id(db: Session, id_vacuna: int) -> Optional[Vacuna]:
    """Busca una vacuna por su ID."""
    return db.query(Vacuna).filter(Vacuna.id_vacuna == id_vacuna).first()


def get_vacunas_by_mascota(db: Session, id_mascota: int) -> List[Vacuna]:
    """Lista las vacunas de una mascota. No hay filtro de 'activo': esta tabla no tiene ese campo."""
    return db.query(Vacuna).filter(Vacuna.id_mascota == id_mascota).all()


def create_vacuna(db: Session, vacuna_data: VacunaCreate) -> Vacuna:
    """Registra una nueva vacuna aplicada."""
    nueva_vacuna = Vacuna(**vacuna_data.model_dump())
    db.add(nueva_vacuna)
    db.commit()
    db.refresh(nueva_vacuna)
    return nueva_vacuna


def update_vacuna(db: Session, vacuna: Vacuna, vacuna_data: VacunaUpdate) -> Vacuna:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = vacuna_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(vacuna, campo, valor)
    db.commit()
    db.refresh(vacuna)
    return vacuna


def eliminar_vacuna(db: Session, vacuna: Vacuna) -> None:
    """Borrado físico: esta tabla no tiene campo 'activo' para soft-delete."""
    db.delete(vacuna)
    db.commit()