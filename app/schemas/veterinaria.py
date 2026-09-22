from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VeterinariaBase(BaseModel):
    nombre_comercial: str
    direccion: str
    telefono: str
    correo_electronico: Optional[str] = None
    horario_atencion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None


class VeterinariaCreate(VeterinariaBase):
    pass


class VeterinariaUpdate(BaseModel):
    nombre_comercial: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    horario_atencion: Optional[str] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    activo: Optional[bool] = None


class VeterinariaResponse(VeterinariaBase):
    model_config = ConfigDict(from_attributes=True)

    id_veterinaria: int
    calificacion_promedio: Decimal
    activo: bool