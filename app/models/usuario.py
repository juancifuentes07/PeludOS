from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_completo = Column(String(100), nullable=False)
    correo_electronico = Column(String(100), nullable=False, unique=True, index=True)
    contrasena_hash = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    direccion = Column(Text, nullable=True)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    rol = Column(String(20), nullable=False, default="cliente")
    activo = Column(Boolean, nullable=False, default=True)