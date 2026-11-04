from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MedicamentoBase(BaseModel):
    id_mascota: int
    id_recordatorio: Optional[int] = None
    nombre_medicamento: str
    dosis: Optional[str] = None
    unidad_medida: Optional[str] = None
    frecuencia_administracion: Optional[str] = None
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = None


class MedicamentoCreate(MedicamentoBase):
    pass


class MedicamentoUpdate(BaseModel):
    id_recordatorio: Optional[int] = None
    nombre_medicamento: Optional[str] = None
    dosis: Optional[str] = None
    unidad_medida: Optional[str] = None
    frecuencia_administracion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None


class MedicamentoResponse(MedicamentoBase):
    model_config = ConfigDict(from_attributes=True)

    id_medicamento: int
    activo: bool