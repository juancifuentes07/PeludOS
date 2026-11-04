from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class CarritoCompras(Base):
    __tablename__ = "carrito_compras"

    id_carrito = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    estado = Column(String(20), nullable=False, default="activo")

    detalles = relationship("DetalleCarrito", backref="carrito", cascade="all, delete-orphan")


class DetalleCarrito(Base):
    __tablename__ = "detalle_carrito"

    id_detalle_carrito = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_carrito = Column(Integer, ForeignKey("carrito_compras.id_carrito"), nullable=False, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)

    producto = relationship("Producto")