import os
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from jwt import JWT, jwk_from_dict
from passlib.context import CryptContext

from app.db.models import User
from app.db.session import get_db


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

bearer_scheme = HTTPBearer(auto_error=False)
token_service = JWT()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _build_symmetric_key(secret: str):
    key_material = (
        base64.urlsafe_b64encode(secret.encode("utf-8"))
        .rstrip(b"=")
        .decode("ascii")
    )

    return jwk_from_dict(
        {
            "kty": "oct",
            "k": key_material,
        }
    )


JWT_KEY = _build_symmetric_key(SECRET_KEY)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update(
        {
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
    )
    return token_service.encode(payload, JWT_KEY, alg=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return token_service.decode(token, JWT_KEY, algorithms={ALGORITHM})


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username.strip()).first()
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user


def load_current_user(db: Session, token: str) -> dict:
    payload = decode_access_token(token)

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    cached_user = getattr(request.state, "current_user", None)
    if cached_user:
        return cached_user

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = load_current_user(db, credentials.credentials)
        request.state.current_user = user
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
