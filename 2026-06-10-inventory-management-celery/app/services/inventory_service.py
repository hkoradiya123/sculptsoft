from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas import InventoryCreate, InventoryUpdate
from app.models.inventory import Inventory as InventoryModel


def get_inventory_or_404(session: Session, inventory_id: int) -> InventoryModel:
    inventory = session.get(InventoryModel, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


def list_inventories(session: Session) -> list[InventoryModel]:
    return session.query(InventoryModel).order_by(InventoryModel.inventory_id).all()


def create_inventory(session: Session, payload: InventoryCreate) -> InventoryModel:
    inventory = InventoryModel(**payload.dict())
    session.add(inventory)
    session.commit()
    session.refresh(inventory)
    return inventory


def update_inventory(
    session: Session, inventory: InventoryModel, payload: InventoryUpdate
) -> InventoryModel:
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(inventory, key, value)
    session.commit()
    session.refresh(inventory)
    return inventory


def delete_inventory(session: Session, inventory: InventoryModel) -> None:
    session.delete(inventory)
    session.commit()

