from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.pedido import Pedido
from app.schemas.pedido import PedidoUpdate


def get_pedido_by_id(db: Session, id_pedido: int) -> Optional[Pedido]:
    """Busca un pedido por su ID."""
    return db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()


def get_pedidos_by_usuario(db: Session, id_usuario: int) -> List[Pedido]:
    """Lista los pedidos de un usuario."""
    return db.query(Pedido).filter(Pedido.id_usuario == id_usuario).all()


def create_pedido(
    db: Session,
    id_usuario: int,
    id_veterinaria: int,
    id_carrito: int,
    total: Decimal,
    direccion_entrega: str,
    metodo_pago: Optional[str],
    notas: Optional[str],
) -> Pedido:
    """Crea un nuevo pedido a partir de un carrito ya finalizado."""
    nuevo_pedido = Pedido(
        id_usuario=id_usuario,
        id_veterinaria=id_veterinaria,
        id_carrito=id_carrito,
        total=total,
        direccion_entrega=direccion_entrega,
        metodo_pago=metodo_pago,
        notas=notas,
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido


def update_pedido(db: Session, pedido: Pedido, pedido_data: PedidoUpdate) -> Pedido:
    """Actualiza solo los campos que vienen con valor (actualización parcial)."""
    datos = pedido_data.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(pedido, campo, valor)
    db.commit()
    db.refresh(pedido)
    return pedido