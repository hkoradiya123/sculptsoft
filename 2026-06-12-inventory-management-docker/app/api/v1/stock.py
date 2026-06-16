from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.dbhelper import get_db
from app.core.auth import admin_required, get_current_user
from app.schemas import StockCreate, StockRead, StockUpdate
from app.services.inventory_service import get_inventory_or_404
from app.services.stock_service import (
    add_stock,
    delete_stock,
    get_stock_or_404,
    list_stock,
    update_stock,
)

router = APIRouter(prefix="/inventories/{inventory_id}/stock", tags=["stock"])


@router.get("", response_model=List[StockRead])
def list_inventory_stock(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    return list_stock(session, inventory_id)


@router.post("", response_model=StockRead, status_code=status.HTTP_201_CREATED, summary="Add Stock (Celery)")
def add_inventory_stock(
    inventory_id: int,
    payload: StockCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    (Celery) Add new stock. Triggers low-stock alert check in background.
    """
    get_inventory_or_404(session, inventory_id)
    return add_stock(session, inventory_id, payload)


@router.patch("/{stock_id}", response_model=StockRead, summary="Update Stock (Celery)")
def update_inventory_stock(
    inventory_id: int,
    stock_id: int,
    payload: StockUpdate,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """
    (Celery) Update existing stock. Triggers low-stock alert check in background.
    """
    get_inventory_or_404(session, inventory_id)
    stock = get_stock_or_404(session, inventory_id, stock_id)
    return update_stock(session, stock, payload)


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_stock(
    inventory_id: int,
    stock_id: int,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    get_inventory_or_404(session, inventory_id)
    stock = get_stock_or_404(session, inventory_id, stock_id)
    delete_stock(session, stock)
    return None

