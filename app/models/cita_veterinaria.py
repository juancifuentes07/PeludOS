from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class CitaVeterinaria(Base):
    __tablename__ = "citas_veterinarias"

    id_cita = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    id_profesional = Column(Integer, ForeignKey("profesionales.id_profesional"), nullable=False, index=True)
    id_veterinaria = Column(Integer, ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    fecha_cita = Column(DateTime(timezone=True), nullable=False)
    motivo = Column(String(200), nullable=False)
    estado = Column(String(20), nullable=False, default="programada")
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    mascota = relationship("Mascota", backref="citas_veterinarias")
    profesional = relationship("Profesional", backref="citas_veterinarias")
    veterinaria = relationship("Veterinaria", backref="citas_veterinarias")