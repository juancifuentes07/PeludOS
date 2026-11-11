from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.carrito import CarritoCompras, DetalleCarrito
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.schemas.pedido import PedidoCreate, PedidoUpdate


def get_pedido_by_id(db: Session, id_pedido: int) -> Optional[Pedido]:
    """Busca un pedido por su ID."""
    return db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()


def get_pedidos_by_usuario(db: Session, id_usuario: int) -> List[Pedido]:
    """Lista los pedidos de un usuario."""
    return db.query(Pedido).filter(Pedido.id_usuario == id_usuario).all()


def get_items_by_pedido(db: Session, pedido: Pedido) -> List[DetalleCarrito]:
    """Devuelve las líneas del carrito (ya finalizado) con el que se generó el pedido."""
    return db.query(DetalleCarrito).filter(DetalleCarrito.id_carrito == pedido.id_carrito).all()


def crear_pedido_desde_carrito(
    db: Session, carrito: CarritoCompras, id_usuario: int, pedido_data: PedidoCreate
) -> Pedido:
    """
    Genera el pedido a partir del carrito en UNA sola transacción: valida y
    descuenta el stock de cada producto, crea el pedido y finaliza el carrito.
    Lanza ValueError si algún producto ya no está disponible o no alcanza el
    stock; en ese caso no se guarda nada (el router hace el rollback).
    """
    id_veterinaria = carrito.detalles[0].producto.id_veterinaria
    total = Decimal("0")

    for detalle in carrito.detalles:
        # Bloquea la fila del producto hasta el commit, para que dos compras
        # simultáneas no vendan el mismo stock. populate_existing fuerza a
        # leer el stock real y no el que ya estaba cargado en la sesión.
        producto = (
            db.query(Producto)
            .filter(Producto.id_producto == detalle.id_producto)
            .populate_existing()
            .with_for_update()
            .first()
        )
        if producto is None or not producto.activo:
            raise ValueError(f"El producto '{detalle.producto.nombre_producto}' ya no está disponible")
        if producto.stock < detalle.cantidad:
            raise ValueError(
                f"Stock insuficiente para '{producto.nombre_producto}' (quedan {producto.stock})"
            )
        producto.stock -= detalle.cantidad
        total += detalle.subtotal

    nuevo_pedido = Pedido(
        id_usuario=id_usuario,
        id_veterinaria=id_veterinaria,
        id_carrito=carrito.id_carrito,
        total=total,
        direccion_entrega=pedido_data.direccion_entrega,
        metodo_pago=pedido_data.metodo_pago,
        notas=pedido_data.notas,
    )
    db.add(nuevo_pedido)
    carrito.estado = "finalizado"
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