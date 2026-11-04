from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductoBase(BaseModel):
    id_veterinaria: int
    nombre_producto: str
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    precio_compra: Decimal
    precio_venta: Decimal
    stock: int = 0
    unidad_medida: Optional[str] = None
    imagen_url: Optional[str] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre_producto: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    precio_compra: Optional[Decimal] = None
    precio_venta: Optional[Decimal] = None
    stock: Optional[int] = None
    unidad_medida: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None


class ProductoResponse(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id_producto: int
    activo: bool