from typing import Optional

from pydantic import BaseModel, Field, ConfigDict 


class InventoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    area: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    area: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)


class InventoryRead(InventoryBase):
    inventory_id: int
    model_config = ConfigDict(from_attributes=True)

