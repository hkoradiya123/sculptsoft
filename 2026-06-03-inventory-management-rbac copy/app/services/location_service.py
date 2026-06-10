from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas import LocationCreate, LocationUpdate
from app.models.inventory import Location as LocationModel


def get_location_or_404(
    session: Session, inventory_id: int, location_id: int
) -> LocationModel:
    location = session.get(LocationModel, location_id)
    if location is None or location.inventory_id != inventory_id:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


def list_locations(session: Session, inventory_id: int) -> list[LocationModel]:
    return (
        session.query(LocationModel)
        .filter(LocationModel.inventory_id == inventory_id)
        .order_by(LocationModel.location_id)
        .all()
    )


def create_location(
    session: Session, inventory_id: int, payload: LocationCreate
) -> LocationModel:
    location = LocationModel(inventory_id=inventory_id, **payload.dict())
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


def update_location(
    session: Session, location: LocationModel, payload: LocationUpdate
) -> LocationModel:
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(location, key, value)
    session.commit()
    session.refresh(location)
    return location


def delete_location(session: Session, location: LocationModel) -> None:
    session.delete(location)
    session.commit()

