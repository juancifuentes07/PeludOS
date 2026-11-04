from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey

from app.database import Base


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id_medicamento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_mascota = Column(Integer, ForeignKey("mascotas.id_mascota"), nullable=False, index=True)
    id_recordatorio = Column(Integer, ForeignKey("recordatorios.id_recordatorio"), nullable=True, index=True)
    nombre_medicamento = Column(String(100), nullable=False)
    dosis = Column(String(50), nullable=True)
    unidad_medida = Column(String(20), nullable=True)
    frecuencia_administracion = Column(String(50), nullable=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)
    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)