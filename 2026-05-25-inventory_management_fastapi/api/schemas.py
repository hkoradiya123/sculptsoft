from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


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

    class Config:
        orm_mode = True


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


class ProductBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)


class ProductCreate(ProductBase):
    name: str = Field(..., max_length=100)
    price: Decimal = Field(..., gt=0)


class ProductUpdate(ProductBase):
    pass


class ProductRead(ProductBase):
    product_id: int

    class Config:
        orm_mode = True


class PriceHistoryRead(BaseModel):
    id: int
    product_id: Optional[int]
    price: Optional[Decimal]
    changed_at: datetime

    class Config:
        orm_mode = True


class StockCreate(BaseModel):
    product_id: int
    location_id: int
    quantity: int = Field(..., ge=0)


class StockUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class StockRead(BaseModel):
    stock_id: int
    product_id: int
    product_name: Optional[str]
    location_id: int
    location_address: Optional[str]
    quantity: Optional[int]

    class Config:
        orm_mode = True
