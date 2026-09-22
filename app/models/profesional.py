from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Profesional(Base):
    __tablename__ = "profesionales"

    id_profesional = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_veterinaria = Column(Integer, ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    nombre_completo = Column(String(100), nullable=False)
    especialidad = Column(String(50), nullable=True)
    numero_registro_profesional = Column(String(30), nullable=True)
    telefono = Column(String(20), nullable=True)
    correo_electronico = Column(String(100), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    veterinaria = relationship("Veterinaria", backref="profesionales")