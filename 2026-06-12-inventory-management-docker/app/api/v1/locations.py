from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.dbhelper import get_db

from app.core.auth import get_current_user
from app.schemas import LocationCreate, LocationRead, LocationUpdate
from app.services.inventory_service import get_inventory_or_404
from app.services.location_service import (
    create_location,
    delete_location,
    get_location_or_404,
    list_locations,
    update_location,
)

router = APIRouter(
    prefix="/inventories/{inventory_id}/locations", tags=["inventories"]
)


@router.get("", response_model=List[LocationRead])
def list_inventory_locations(
    inventory_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    return list_locations(session, inventory_id)


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_inventory_location(
    inventory_id: int,
    payload: LocationCreate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    return create_location(session, inventory_id, payload)


@router.patch("/{location_id}", response_model=LocationRead)
def update_inventory_location(
    inventory_id: int,
    location_id: int,
    payload: LocationUpdate,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    location = get_location_or_404(session, inventory_id, location_id)
    return update_location(session, location, payload)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_location(
    inventory_id: int,
    location_id: int,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_inventory_or_404(session, inventory_id)
    location = get_location_or_404(session, inventory_id, location_id)
    delete_location(session, location)
    return None

