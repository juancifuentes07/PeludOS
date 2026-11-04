from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_veterinaria = Column(Integer, ForeignKey("veterinarias.id_veterinaria"), nullable=False, index=True)
    id_carrito = Column(Integer, ForeignKey("carrito_compras.id_carrito"), nullable=False, index=True)
    fecha_pedido = Column(DateTime(timezone=True), server_default=func.now())
    total = Column(DECIMAL(10, 2), nullable=False)
    estado_pedido = Column(String(30), nullable=False, default="pendiente")
    metodo_pago = Column(String(30), nullable=True)
    direccion_entrega = Column(Text, nullable=False)
    notas = Column(Text, nullable=True)
    fecha_entrega = Column(DateTime(timezone=True), nullable=True)