from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.pedido import (
    PedidoCreate,
    PedidoDetalleResponse,
    PedidoItemResponse,
    PedidoResponse,
    PedidoUpdate,
)
from app.crud.carrito import get_carrito_activo
from app.crud.pedido import (
    get_pedido_by_id,
    get_pedidos_by_usuario,
    get_items_by_pedido,
    crear_pedido_desde_carrito,
    update_pedido,
)
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=List[PedidoResponse])
def read_pedidos(
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista los pedidos del usuario autenticado."""
    return get_pedidos_by_usuario(db, usuario_actual.id_usuario)


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    pedido_data: PedidoCreate,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Genera un pedido a partir del carrito activo del usuario autenticado.
    Valida y descuenta el stock, calcula el total y finaliza el carrito, todo
    en una sola transacción. Si falta stock responde 400 y no se guarda nada.
    """
    carrito = get_carrito_activo(db, usuario_actual.id_usuario)
    if carrito is None or not carrito.detalles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")

    try:
        return crear_pedido_desde_carrito(db, carrito, usuario_actual.id_usuario, pedido_data)
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/{id_pedido}", response_model=PedidoDetalleResponse)
def read_pedido(
    id_pedido: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Devuelve el detalle de un pedido con sus productos. Disponible para el
    dueño del pedido (o para cualquier admin).
    """
    pedido = get_pedido_by_id(db, id_pedido)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if usuario_actual.rol != "admin" and pedido.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    items = [
        PedidoItemResponse(
            id_producto=d.id_producto,
            nombre_producto=d.producto.nombre_producto,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
        )
        for d in get_items_by_pedido(db, pedido)
    ]
    base = PedidoResponse.model_validate(pedido).model_dump()
    return PedidoDetalleResponse(**base, items=items)


@router.patch("/{id_pedido}", response_model=PedidoResponse)
def update_existing_pedido(
    id_pedido: int,
    pedido_data: PedidoUpdate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Actualiza el estado de un pedido (ej. 'confirmado', 'enviado', 'entregado').
    Requiere rol admin. No hay DELETE: los pedidos no se borran, solo cambian de estado.
    """
    pedido = get_pedido_by_id(db, id_pedido)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return update_pedido(db, pedido, pedido_data)