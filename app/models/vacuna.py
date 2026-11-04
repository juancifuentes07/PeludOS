from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.database import Base


class Vacuna(Base):
    __tablename__ = "vacunas"

    id_vacuna = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    id_recordatorio = Column(Integer, ForeignKey("recordatorios.id_recordatorio"), nullable=True, index=True)
    nombre_vacuna = Column(String(100), nullable=False)
    fecha_aplicacion = Column(Date, nullable=False)
    fecha_proxima_dosis = Column(Date, nullable=True)
    numero_dosis = Column(Integer, nullable=False, default=1)
    lote = Column(String(50), nullable=True)
    veterinario_nombre = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())