from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MascotaBase(BaseModel):
    nombre: str
    especie: str
    raza: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    peso_kg: Optional[Decimal] = None
    color_mascota: Optional[str] = None
    numero_chip: Optional[str] = None
    foto_url: Optional[str] = None
    alergias: Optional[str] = None
    condiciones_medicas: Optional[str] = None


class MascotaCreate(MascotaBase):
    pass


class MascotaUpdate(BaseModel):
    nombre: Optional[str] = None
    especie: Optional[str] = None
    raza: Optional[str] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    peso_kg: Optional[Decimal] = None
    color_mascota: Optional[str] = None
    numero_chip: Optional[str] = None
    foto_url: Optional[str] = None
    alergias: Optional[str] = None
    condiciones_medicas: Optional[str] = None
    activo: Optional[bool] = None


class MascotaResponse(MascotaBase):
    model_config = ConfigDict(from_attributes=True)

    id_mascota: int
    id_usuario: int
    activo: bool