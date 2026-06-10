from typing import Literal
from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdate(BaseModel):
    role: Literal["admin", "manager", "viewer"]
