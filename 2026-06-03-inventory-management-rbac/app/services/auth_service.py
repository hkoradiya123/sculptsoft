from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User

DEFAULT_ADMIN_EMAIL = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_ROLE = "admin"


def authenticate_user(session: Session, email: str, password: str) -> str:
    user = session.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token({"sub": str(user.id), "role": user.role.lower()})


def register_user(session: Session, payload: RegisterRequest) -> None:
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    try:
        session.commit()
        session.refresh(user)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from exc


def ensure_default_admin(session: Session) -> None:
    admin = session.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
    if admin:
        admin.hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)
        admin.role = DEFAULT_ADMIN_ROLE
        return

    session.add(
        User(
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            role=DEFAULT_ADMIN_ROLE,
        )
    )

