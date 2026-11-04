from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.pedido import PedidoCreate, PedidoResponse, PedidoUpdate
from app.crud.carrito import get_carrito_activo, finalizar_carrito
from app.crud.pedido import get_pedido_by_id, get_pedidos_by_usuario, create_pedido, update_pedido
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
    El total se calcula sumando los subtotales del carrito, nunca se recibe
    del cliente. El carrito queda 'finalizado' y el usuario empieza uno
    nuevo la próxima vez que agregue un producto.
    """
    carrito = get_carrito_activo(db, usuario_actual.id_usuario)
    if carrito is None or not carrito.detalles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")

    id_veterinaria = carrito.detalles[0].producto.id_veterinaria
    total = sum((detalle.subtotal for detalle in carrito.detalles), Decimal("0"))

    nuevo_pedido = create_pedido(
        db,
        id_usuario=usuario_actual.id_usuario,
        id_veterinaria=id_veterinaria,
        id_carrito=carrito.id_carrito,
        total=total,
        direccion_entrega=pedido_data.direccion_entrega,
        metodo_pago=pedido_data.metodo_pago,
        notas=pedido_data.notas,
    )
    finalizar_carrito(db, carrito)
    return nuevo_pedido


@router.get("/{id_pedido}", response_model=PedidoResponse)
def read_pedido(
    id_pedido: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el detalle de un pedido del usuario autenticado (o de cualquiera, si es admin)."""
    pedido = get_pedido_by_id(db, id_pedido)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if usuario_actual.rol != "admin" and pedido.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return pedido


@router.patch("/{id_pedido}", response_model=PedidoResponse)
def update_existing_pedido(
    id_pedido: int,
    pedido_data: PedidoUpdate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Actualiza el estado de un pedido (ej. 'confirmado', 'enviado', 'entregado').
    Requiere rol admin: el cliente no puede cambiar el estado de su propio
    pedido directamente. No hay DELETE en este módulo — los pedidos no se
    borran, solo cambian de estado.
    """
    pedido = get_pedido_by_id(db, id_pedido)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return update_pedido(db, pedido, pedido_data)