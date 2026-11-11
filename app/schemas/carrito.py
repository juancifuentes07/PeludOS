from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class AgregarItemCarrito(BaseModel):
    id_producto: int
    cantidad: int = 1


class ActualizarItemCarrito(BaseModel):
    cantidad: int


class DetalleCarritoResponse(BaseModel):
    id_detalle_carrito: int
    id_producto: int
    nombre_producto: str
    imagen_url: Optional[str] = None
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class CarritoResponse(BaseModel):
    """
    'total' no es una columna real de CarritoCompras: se calcula sumando
    los subtotales y se arma manualmente en el router (_build_carrito_response).
    """
    id_carrito: int
    id_usuario: int
    estado: str
    fecha_creacion: datetime
    detalles: List[DetalleCarritoResponse] = []
    total: Decimal