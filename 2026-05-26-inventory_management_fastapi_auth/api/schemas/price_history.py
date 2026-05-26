from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class PriceHistoryRead(BaseModel):
    id: int
    product_id: Optional[int]
    price: Optional[Decimal]
    changed_at: datetime

    class Config:
        orm_mode = True
