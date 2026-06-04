from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

class UserRead(BaseModel):
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)