from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.recordatorio import Recordatorio
from app.schemas.recordatorio import RecordatorioCreate, RecordatorioUpdate


def get_recordatorio_by_id(db: Session, id_recordatorio: int) -> Optional[Recordatorio]:
    """Busca un recordatorio por su ID."""
    return db.query(Recordatorio).filter(Recordatorio.id_recordatorio == id_recordatorio).first()


def get_recordatorios_by_mascota(db: Session, id_mascota: int) -> List[Recordatorio]:
    """Lista los recordatorios activos de una mascota."""
    return (
        db.query(Recordatorio)
        .filter(Recordatorio.id_mascota == id_mascota, Recordatorio.activo.is_(True))
        .all()
    )


def create_recordatorio(db: Session, recordatorio_data: RecordatorioCreate) -> Recordatorio:
    """Crea un nuevo recordatorio."""
    nuevo_recordatorio = Recordatorio(**recordatorio_data.model_dump())
    db.add(nuevo_recordatorio)
    db.commit()
    db.refresh(nuevo_recordatorio)
    return nuevo_recordatorio


def update_recordatorio(db: Session, recordatorio: Recordatorio, recordatorio_data: RecordatorioUpdate) -> Recordatorio:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = recordatorio_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(recordatorio, campo, valor)
    db.commit()
    db.refresh(recordatorio)
    return recordatorio


def desactivar_recordatorio(db: Session, recordatorio: Recordatorio) -> Recordatorio:
    """Soft delete: marca el recordatorio como inactivo en vez de borrarlo físicamente."""
    recordatorio.activo = False
    db.commit()
    db.refresh(recordatorio)
    return recordatorio