from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .models import Sex


class PersonBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0)
    sex: Sex


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    country: Optional[str] = Field(default=None, min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, ge=0)
    sex: Optional[Sex] = None


class PersonOut(PersonBase):
    id: int

    class Config:
        orm_mode = True


class PageResponse(BaseModel):
    page_number: int
    page_size: int
    total_pages: int
    total_records: int
    content: List[Any]
