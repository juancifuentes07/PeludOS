from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProfesionalBase(BaseModel):
    nombre_completo: str
    especialidad: Optional[str] = None
    numero_registro_profesional: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None


class ProfesionalCreate(ProfesionalBase):
    pass


class ProfesionalUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    especialidad: Optional[str] = None
    numero_registro_profesional: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    activo: Optional[bool] = None


class ProfesionalResponse(ProfesionalBase):
    model_config = ConfigDict(from_attributes=True)

    id_profesional: int
    id_veterinaria: int
    activo: bool