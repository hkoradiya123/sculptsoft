from pydantic import BaseModel


class PersonCreate(BaseModel):
    name: str
    age: int
    country: str


class PersonResponse(BaseModel):
    id: int
    name: str
    age: int
    country: str

    class Config:
        from_attributes = True
