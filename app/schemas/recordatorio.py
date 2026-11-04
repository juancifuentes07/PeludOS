from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RecordatorioBase(BaseModel):
    id_mascota: int
    titulo: str
    descripcion: Optional[str] = None
    tipo: str
    fecha_programada: datetime
    frecuencia: Optional[str] = None


class RecordatorioCreate(RecordatorioBase):
    pass


class RecordatorioUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    frecuencia: Optional[str] = None
    notificado: Optional[bool] = None
    activo: Optional[bool] = None


class RecordatorioResponse(RecordatorioBase):
    model_config = ConfigDict(from_attributes=True)

    id_recordatorio: int
    notificado: bool
    fecha_notificacion: Optional[datetime] = None
    activo: bool
    fecha_creacion: datetime