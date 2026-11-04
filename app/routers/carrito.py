from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.carrito import AgregarItemCarrito, ActualizarItemCarrito, CarritoResponse, DetalleCarritoResponse
from app.crud.producto import get_producto_by_id
from app.crud.carrito import (
    get_or_create_carrito_activo,
    get_detalle_by_id,
    agregar_item,
    actualizar_cantidad_item,
    eliminar_item,
    vaciar_carrito,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/carrito", tags=["Carrito de Compras"])


def _build_carrito_response(carrito) -> CarritoResponse:
    """Arma la respuesta del carrito incluyendo sus líneas y el total calculado."""
    detalles = [DetalleCarritoResponse.model_validate(d) for d in carrito.detalles]
    total = sum((d.subtotal for d in detalles), Decimal("0"))
    return CarritoResponse(
        id_carrito=carrito.id_carrito,
        id_usuario=carrito.id_usuario,
        estado=carrito.estado,
        fecha_creacion=carrito.fecha_creacion,
        detalles=detalles,
        total=total,
    )


@router.get("/", response_model=CarritoResponse)
def read_carrito(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el carrito activo del usuario autenticado (lo crea vacío si no tiene uno)."""
    carrito = get_or_create_carrito_activo(db, usuario_actual.id_usuario)
    return _build_carrito_response(carrito)


@router.post("/items", response_model=CarritoResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_carrito(
    item_data: AgregarItemCarrito,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Agrega un producto al carrito activo del usuario (o incrementa su cantidad
    si ya estaba). El carrito solo admite productos de una misma veterinaria:
    si intentas agregar uno de otra, se rechaza hasta que vacíes el carrito.
    """
    if item_data.cantidad < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser al menos 1")

    producto = get_producto_by_id(db, item_data.id_producto)
    if producto is None or not producto.activo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    if producto.stock < item_data.cantidad:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente")

    carrito = get_or_create_carrito_activo(db, usuario_actual.id_usuario)

    if carrito.detalles:
        veterinaria_actual = carrito.detalles[0].producto.id_veterinaria
        if producto.id_veterinaria != veterinaria_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carrito solo puede tener productos de una misma veterinaria. Vacíalo antes de agregar productos de otra.",
            )

    agregar_item(db, carrito, producto, item_data.cantidad)
    db.refresh(carrito)
    return _build_carrito_response(carrito)


@router.patch("/items/{id_detalle_carrito}", response_model=CarritoResponse)
def update_item_carrito(
    id_detalle_carrito: int,
    item_data: ActualizarItemCarrito,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza la cantidad de una línea del carrito del usuario autenticado."""
    if item_data.cantidad < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser al menos 1")

    carrito = get_or_create_carrito_activo(db, usuario_actual.id_usuario)
    detalle = get_detalle_by_id(db, id_detalle_carrito)
    if detalle is None or detalle.id_carrito != carrito.id_carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado en el carrito")

    actualizar_cantidad_item(db, detalle, item_data.cantidad)
    db.refresh(carrito)
    return _build_carrito_response(carrito)


@router.delete("/items/{id_detalle_carrito}", response_model=CarritoResponse)
def remove_item_from_carrito(
    id_detalle_carrito: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Elimina una línea del carrito del usuario autenticado."""
    carrito = get_or_create_carrito_activo(db, usuario_actual.id_usuario)
    detalle = get_detalle_by_id(db, id_detalle_carrito)
    if detalle is None or detalle.id_carrito != carrito.id_carrito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado en el carrito")

    eliminar_item(db, detalle)
    db.refresh(carrito)
    return _build_carrito_response(carrito)


@router.delete("/", response_model=CarritoResponse)
def clear_carrito(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Vacía el carrito activo del usuario autenticado, sin cambiar su estado."""
    carrito = get_or_create_carrito_activo(db, usuario_actual.id_usuario)
    vaciar_carrito(db, carrito)
    db.refresh(carrito)
    return _build_carrito_response(carrito)