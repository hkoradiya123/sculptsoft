from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.dbhelper import get_db
from app.core.auth import admin_required, get_current_user
from app.schemas import InventoryCreate, InventoryRead, InventoryUpdate
from app.services.inventory_service import (
    create_inventory,
    delete_inventory,
    get_inventory_or_404,
    list_inventories,
    update_inventory,
)
from app.tasks.inventory_tasks import generate_inventory_report

router = APIRouter(prefix="/inventories", tags=["inventories"])


@router.post("/{inventory_id}/generate-report", status_code=status.HTTP_202_ACCEPTED, summary="Generate Report (Celery)")
def trigger_report(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    (Celery) Trigger a background report generation task.
    Returns a task_id to track progress.
    """
    get_inventory_or_404(session, inventory_id) # Ensure inventory exists
    task = generate_inventory_report.delay(inventory_id)
    return {"task_id": task.id, "status": "Processing"}


@router.get("", response_model=List[InventoryRead])
def list_inventory(
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ):
    return list_inventories(session)


@router.post("", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ):
    return create_inventory(session, payload)


@router.get("/{inventory_id}", response_model=InventoryRead)
def get_inventory(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ):
    return get_inventory_or_404(session, inventory_id)


@router.patch("/{inventory_id}", response_model=InventoryRead)
def update_inventory_item(
    inventory_id: int,
    payload: InventoryUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ):
    inventory = get_inventory_or_404(session, inventory_id)
    return update_inventory(session, inventory, payload)


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    inventory_id: int,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
    ):
    inventory = get_inventory_or_404(session, inventory_id)
    delete_inventory(session, inventory)
    return None

    return None

