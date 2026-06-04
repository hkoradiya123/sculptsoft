from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.dbhelper import get_db
from app.core.auth import get_current_user
from app.schemas.auth import RegisterRequest, ChangePasswordRequest, LoginRequest
from app.services.auth_service import authenticate_user, register_user
from app.services.user_service import change_user_password

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(
    payload: LoginRequest,
    session: Session = Depends(get_db),
    ):
    token = authenticate_user(session, payload.email, payload.password)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: Session = Depends(get_db)):
    register_user(session, payload)
    return {"message": "User created"}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    change_user_password(
        session, 
        current_user["id"], 
        payload.old_password, 
        payload.new_password
    )
    return {"message": "Password updated successfully"}
