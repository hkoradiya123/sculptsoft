from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.dbhelper import get_db
from app.core.auth import admin_required
from app.schemas import UserRead, UserRoleUpdate
from app.schemas.auth import AdminResetPasswordRequest
from app.models.user import User
from app.services.user_service import admin_reset_password

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
    ):
    return session.query(User).all()

# @router.post("/users", response_model=List[UserRead])
# def add_users(
#     session: Session = Depends(get_db),
#     admin=Depends(admin_required),
#     ):
    


@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
    ):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = payload.role
    session.commit()
    session.refresh(user)
    return user


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    session: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    admin_reset_password(session, user_id, payload.new_password)
    return {"message": "User password reset successfully"}
