from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.medicamento import Medicamento
from app.schemas.medicamento import MedicamentoCreate, MedicamentoUpdate


def get_medicamento_by_id(db: Session, id_medicamento: int) -> Optional[Medicamento]:
    """Busca un medicamento por su ID."""
    return db.query(Medicamento).filter(Medicamento.id_medicamento == id_medicamento).first()


def get_medicamentos_by_mascota(db: Session, id_mascota: int) -> List[Medicamento]:
    """Lista los medicamentos activos de una mascota."""
    return (
        db.query(Medicamento)
        .filter(Medicamento.id_mascota == id_mascota, Medicamento.activo.is_(True))
        .all()
    )


def create_medicamento(db: Session, medicamento_data: MedicamentoCreate) -> Medicamento:
    """Crea un nuevo medicamento."""
    nuevo_medicamento = Medicamento(**medicamento_data.model_dump())
    db.add(nuevo_medicamento)
    db.commit()
    db.refresh(nuevo_medicamento)
    return nuevo_medicamento


def update_medicamento(db: Session, medicamento: Medicamento, medicamento_data: MedicamentoUpdate) -> Medicamento:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = medicamento_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(medicamento, campo, valor)
    db.commit()
    db.refresh(medicamento)
    return medicamento


def desactivar_medicamento(db: Session, medicamento: Medicamento) -> Medicamento:
    """Soft delete: marca el medicamento como inactivo en vez de borrarlo físicamente."""
    medicamento.activo = False
    db.commit()
    db.refresh(medicamento)
    return medicamento