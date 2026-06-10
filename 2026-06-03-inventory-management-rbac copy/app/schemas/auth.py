from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", example="user@example.com")
    password: str = Field(..., min_length=6, max_length=72, example="strongpassword")

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", example="user@example.com")
    password: str = Field(..., min_length=6, max_length=72, example="strongpassword") 
    role: Literal["admin", "manager", "viewer"] = "viewer"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=72)
    new_password: str = Field(..., min_length=6, max_length=72)


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=72)

