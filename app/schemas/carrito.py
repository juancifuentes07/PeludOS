from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict


class AgregarItemCarrito(BaseModel):
    id_producto: int
    cantidad: int = 1


class ActualizarItemCarrito(BaseModel):
    cantidad: int


class DetalleCarritoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_detalle_carrito: int
    id_producto: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class CarritoResponse(BaseModel):
    """
    No hereda de un modelo con from_attributes porque 'total' no es una
    columna real de CarritoCompras: se calcula sumando los subtotales
    y se arma manualmente en el router (ver _build_carrito_response).
    """
    id_carrito: int
    id_usuario: int
    estado: str
    fecha_creacion: datetime
    detalles: List[DetalleCarritoResponse] = []
    total: Decimal