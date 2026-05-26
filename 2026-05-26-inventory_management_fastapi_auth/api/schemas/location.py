from typing import Optional

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    address: Optional[str] = Field(None, max_length=150)


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    pass


class LocationRead(LocationBase):
    location_id: int
    inventory_id: int

    class Config:
        orm_mode = True
