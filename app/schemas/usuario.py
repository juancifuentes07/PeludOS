from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UsuarioBase(BaseModel):
    """Campos comunes compartidos entre creación y lectura."""
    nombre_completo: str
    correo_electronico: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    """Lo que se recibe al registrar un usuario (incluye password en texto plano, solo de entrada)."""
    contrasena: str


class UsuarioUpdate(BaseModel):
    """Campos que un usuario puede actualizar de su propio perfil. Todos opcionales."""
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    """Lo que se devuelve al cliente. NUNCA incluye contrasena_hash."""
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    rol: str
    activo: bool
    fecha_registro: datetime


class UsuarioLogin(BaseModel):
    """Lo que se recibe al hacer login."""
    correo_electronico: EmailStr
    contrasena: str


class Token(BaseModel):
    """Lo que se devuelve tras un login exitoso."""
    access_token: str
    token_type: str = "bearer"