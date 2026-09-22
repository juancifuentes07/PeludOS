from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Mascota(Base):
    __tablename__ = "mascotas"

    id_mascota = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    nombre = Column(String(50), nullable=False)
    especie = Column(String(30), nullable=False)
    raza = Column(String(50), nullable=True)
    sexo = Column(String(10), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    peso_kg = Column(DECIMAL(5, 2), nullable=True)
    color_mascota = Column(String(30), nullable=True)
    numero_chip = Column(String(50), unique=True, nullable=True)
    foto_url = Column(Text, nullable=True)
    alergias = Column(Text, nullable=True)
    condiciones_medicas = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    propietario = relationship("Usuario", backref="mascotas")