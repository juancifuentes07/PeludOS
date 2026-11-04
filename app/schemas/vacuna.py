from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VacunaBase(BaseModel):
    id_mascota: int
    id_recordatorio: Optional[int] = None
    nombre_vacuna: str
    fecha_aplicacion: date
    fecha_proxima_dosis: Optional[date] = None
    numero_dosis: int = 1
    lote: Optional[str] = None
    veterinario_nombre: Optional[str] = None


class VacunaCreate(VacunaBase):
    pass


class VacunaUpdate(BaseModel):
    id_recordatorio: Optional[int] = None
    nombre_vacuna: Optional[str] = None
    fecha_aplicacion: Optional[date] = None
    fecha_proxima_dosis: Optional[date] = None
    numero_dosis: Optional[int] = None
    lote: Optional[str] = None
    veterinario_nombre: Optional[str] = None


class VacunaResponse(VacunaBase):
    model_config = ConfigDict(from_attributes=True)

    id_vacuna: int
    fecha_creacion: datetime