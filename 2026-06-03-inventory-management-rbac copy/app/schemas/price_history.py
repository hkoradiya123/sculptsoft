from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PriceHistoryRead(BaseModel):
    id: int
    product_id: Optional[int]
    price: Optional[Decimal]
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)

