from typing import Optional

from sqlalchemy.orm import Session

from app.models.carrito import CarritoCompras, DetalleCarrito
from app.models.producto import Producto


def get_carrito_activo(db: Session, id_usuario: int) -> Optional[CarritoCompras]:
    """Busca el carrito activo del usuario, si existe."""
    return (
        db.query(CarritoCompras)
        .filter(CarritoCompras.id_usuario == id_usuario, CarritoCompras.estado == "activo")
        .first()
    )


def get_or_create_carrito_activo(db: Session, id_usuario: int) -> CarritoCompras:
    """Devuelve el carrito activo del usuario, o crea uno nuevo si no tiene."""
    carrito = get_carrito_activo(db, id_usuario)
    if carrito is None:
        carrito = CarritoCompras(id_usuario=id_usuario, estado="activo")
        db.add(carrito)
        db.commit()
        db.refresh(carrito)
    return carrito


def get_detalle_by_id(db: Session, id_detalle_carrito: int) -> Optional[DetalleCarrito]:
    """Busca una línea del carrito por su ID."""
    return db.query(DetalleCarrito).filter(DetalleCarrito.id_detalle_carrito == id_detalle_carrito).first()


def get_detalle_by_producto(db: Session, id_carrito: int, id_producto: int) -> Optional[DetalleCarrito]:
    """Busca si un producto ya está agregado en el carrito."""
    return (
        db.query(DetalleCarrito)
        .filter(DetalleCarrito.id_carrito == id_carrito, DetalleCarrito.id_producto == id_producto)
        .first()
    )


def agregar_item(db: Session, carrito: CarritoCompras, producto: Producto, cantidad: int) -> DetalleCarrito:
    """
    Agrega un producto al carrito, o incrementa la cantidad si ya estaba.
    precio_unitario y subtotal se calculan aquí a partir del precio_venta
    del producto, nunca se reciben del cliente.
    """
    detalle_existente = get_detalle_by_producto(db, carrito.id_carrito, producto.id_producto)
    if detalle_existente:
        detalle_existente.cantidad += cantidad
        detalle_existente.subtotal = detalle_existente.precio_unitario * detalle_existente.cantidad
        db.commit()
        db.refresh(detalle_existente)
        return detalle_existente

    nuevo_detalle = DetalleCarrito(
        id_carrito=carrito.id_carrito,
        id_producto=producto.id_producto,
        cantidad=cantidad,
        precio_unitario=producto.precio_venta,
        subtotal=producto.precio_venta * cantidad,
    )
    db.add(nuevo_detalle)
    db.commit()
    db.refresh(nuevo_detalle)
    return nuevo_detalle


def actualizar_cantidad_item(db: Session, detalle: DetalleCarrito, cantidad: int) -> DetalleCarrito:
    """Actualiza la cantidad de una línea del carrito y recalcula su subtotal."""
    detalle.cantidad = cantidad
    detalle.subtotal = detalle.precio_unitario * cantidad
    db.commit()
    db.refresh(detalle)
    return detalle


def eliminar_item(db: Session, detalle: DetalleCarrito) -> None:
    """Elimina una línea del carrito."""
    db.delete(detalle)
    db.commit()


def vaciar_carrito(db: Session, carrito: CarritoCompras) -> None:
    """Elimina todas las líneas del carrito, sin cambiar su estado."""
    db.query(DetalleCarrito).filter(DetalleCarrito.id_carrito == carrito.id_carrito).delete()
    db.commit()


def finalizar_carrito(db: Session, carrito: CarritoCompras) -> CarritoCompras:
    """Marca un carrito como finalizado tras generar un pedido a partir de él."""
    carrito.estado = "finalizado"
    db.commit()
    db.refresh(carrito)
    return carrito