from typing import Optional

from pydantic import BaseModel, Field


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

