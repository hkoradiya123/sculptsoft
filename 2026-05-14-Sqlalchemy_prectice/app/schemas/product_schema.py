from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: float
    description: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True
