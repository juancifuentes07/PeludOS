from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Recordatorio(Base):
    __tablename__ = "recordatorios"

    id_recordatorio = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(30), nullable=False)
    fecha_programada = Column(DateTime(timezone=True), nullable=False)
    frecuencia = Column(String(20), nullable=True)
    notificado = Column(Boolean, nullable=False, default=False)
    fecha_notificacion = Column(DateTime(timezone=True), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    mascota = relationship("Mascota", backref="recordatorios")