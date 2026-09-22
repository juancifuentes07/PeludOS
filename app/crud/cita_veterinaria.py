from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.cita_veterinaria import CitaVeterinaria
from app.schemas.cita_veterinaria import CitaVeterinariaCreate, CitaVeterinariaUpdate


def get_cita_by_id(db: Session, id_cita: int) -> Optional[CitaVeterinaria]:
    """Busca una cita por su ID."""
    return db.query(CitaVeterinaria).filter(CitaVeterinaria.id_cita == id_cita).first()


def get_citas_by_mascota(db: Session, id_mascota: int) -> List[CitaVeterinaria]:
    """Lista las citas de una mascota específica."""
    return db.query(CitaVeterinaria).filter(CitaVeterinaria.id_mascota == id_mascota).all()


def get_citas_by_usuario(db: Session, id_usuario: int) -> List[CitaVeterinaria]:
    """Lista todas las citas de las mascotas de un usuario (join contra mascotas)."""
    from app.models.mascota import Mascota

    return (
        db.query(CitaVeterinaria)
        .join(Mascota, CitaVeterinaria.id_mascota == Mascota.id_mascota)
        .filter(Mascota.id_usuario == id_usuario)
        .all()
    )


def create_cita(db: Session, cita_data: CitaVeterinariaCreate) -> CitaVeterinaria:
    """Crea una nueva cita veterinaria."""
    nueva_cita = CitaVeterinaria(**cita_data.model_dump())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


def update_cita(db: Session, cita: CitaVeterinaria, cita_data: CitaVeterinariaUpdate) -> CitaVeterinaria:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = cita_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(cita, campo, valor)
    db.commit()
    db.refresh(cita)
    return cita


def cancelar_cita(db: Session, cita: CitaVeterinaria) -> CitaVeterinaria:
    """Cancela una cita cambiando su estado. No hay borrado físico ni soft-delete con 'activo' en esta tabla."""
    cita.estado = "cancelada"
    db.commit()
    db.refresh(cita)
    return cita