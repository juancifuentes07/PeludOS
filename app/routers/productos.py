from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.producto import ProductoCreate, ProductoResponse, ProductoUpdate
from app.crud.veterinaria import get_veterinaria_by_id
from app.crud.producto import (
    get_producto_by_id,
    get_productos,
    get_productos_by_veterinaria,
    create_producto,
    update_producto,
    desactivar_producto,
)
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=List[ProductoResponse])
def read_productos(
    id_veterinaria: Optional[int] = None,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista los productos activos. Si se pasa id_veterinaria como query param
    (?id_veterinaria=1), filtra solo los de esa veterinaria.
    """
    if id_veterinaria is not None:
        return get_productos_by_veterinaria(db, id_veterinaria)
    return get_productos(db)


@router.get("/{id_producto}", response_model=ProductoResponse)
def read_producto(
    id_producto: int,
    usuario_actual: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve el detalle de un producto."""
    producto = get_producto_by_id(db, id_producto)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def create_new_producto(
    producto_data: ProductoCreate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Registra un nuevo producto. Requiere rol admin."""
    veterinaria = get_veterinaria_by_id(db, producto_data.id_veterinaria)
    if veterinaria is None or not veterinaria.activo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinaria no encontrada")
    return create_producto(db, producto_data)


@router.patch("/{id_producto}", response_model=ProductoResponse)
def update_existing_producto(
    id_producto: int,
    producto_data: ProductoUpdate,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Actualiza un producto (actualización parcial). Requiere rol admin."""
    producto = get_producto_by_id(db, id_producto)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return update_producto(db, producto, producto_data)


@router.delete("/{id_producto}", response_model=ProductoResponse)
def deactivate_producto(
    id_producto: int,
    usuario_actual: Usuario = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Desactiva (soft delete) un producto. Requiere rol admin."""
    producto = get_producto_by_id(db, id_producto)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return desactivar_producto(db, producto)