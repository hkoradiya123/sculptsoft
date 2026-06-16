from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.dbhelper import get_db
from app.core.auth import admin_required, get_current_user
from app.schemas import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import (
    create_product,
    delete_product,
    get_product_or_404,
    list_products,
    update_product,
)
from app.tasks.inventory_tasks import bulk_import_products

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/bulk-import", status_code=status.HTTP_202_ACCEPTED, summary="Bulk Import (Celery)")
def bulk_import(
    payload: List[ProductCreate],
    current_user=Depends(get_current_user),
):
    """
    (Celery) Bulk import products from a list.
    """
    # Convert Pydantic models to dict for Celery serialization
    product_list = [p.dict() for p in payload]
    task = bulk_import_products.delay(product_list)
    return {"task_id": task.id, "status": "Importing"}


@router.get("", response_model=List[ProductRead])
def list_all_products(
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_products(session)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product_item(
    payload: ProductCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_product(session, payload)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_product_or_404(session, product_id)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product_item(
    product_id: int,
    payload: ProductUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = get_product_or_404(session, product_id)
    return update_product(session, product, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_item(
    product_id: int,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    product = get_product_or_404(session, product_id)
    delete_product(session, product)
    return None

