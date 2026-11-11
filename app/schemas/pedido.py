from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PedidoCreate(BaseModel):
    direccion_entrega: str
    metodo_pago: Optional[str] = None
    notas: Optional[str] = None


class PedidoUpdate(BaseModel):
    estado_pedido: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    notas: Optional[str] = None


class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: int
    id_usuario: int
    id_veterinaria: int
    id_carrito: int
    fecha_pedido: datetime
    total: Decimal
    estado_pedido: str
    metodo_pago: Optional[str] = None
    direccion_entrega: str
    notas: Optional[str] = None
    fecha_entrega: Optional[datetime] = None


class PedidoItemResponse(BaseModel):
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class PedidoDetalleResponse(PedidoResponse):
    items: List[PedidoItemResponse] = []