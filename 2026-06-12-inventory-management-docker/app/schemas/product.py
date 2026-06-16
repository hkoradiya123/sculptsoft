from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)

