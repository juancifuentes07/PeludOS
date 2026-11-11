from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class CitaVeterinariaBase(BaseModel):
    id_mascota: int
    id_profesional: int
    id_veterinaria: int
    fecha_cita: datetime
    motivo: str
    notas: Optional[str] = None


class CitaVeterinariaCreate(CitaVeterinariaBase):
    pass


class CitaVeterinariaUpdate(BaseModel):
    fecha_cita: Optional[datetime] = None
    motivo: Optional[str] = None
    notas: Optional[str] = None


class CitaEstadoUpdate(BaseModel):
    estado: Literal["programada", "confirmada", "completada", "cancelada"]


class CitaVeterinariaResponse(CitaVeterinariaBase):
    model_config = ConfigDict(from_attributes=True)

    id_cita: int
    estado: str
    fecha_creacion: datetime
    nombre_mascota: Optional[str] = None
    nombre_veterinaria: Optional[str] = None
    nombre_profesional: Optional[str] = None