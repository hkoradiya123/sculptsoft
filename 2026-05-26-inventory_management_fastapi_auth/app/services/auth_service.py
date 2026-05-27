from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User


def authenticate_user(session: Session, email: str, password: str) -> str:
    user = session.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token({"sub": str(user.id), "role": user.role})


def register_user(session: Session, payload: RegisterRequest) -> None:
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc

