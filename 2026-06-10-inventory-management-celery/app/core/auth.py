from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database.dbhelper import get_db
# from app.api.deps.db import get_db
from app.core.security import decode_access_token
from app.models.user import User


oauth2_scheme = HTTPBearer()


def _normalize_role(role: str | None) -> str:
    return (role or "").strip().lower()


def load_current_user(session: Session, token: str) -> dict:
    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_pk = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = session.query(User).filter(User.id == user_pk).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "role": _normalize_role(user.role),
    }


def get_current_user(
    auth: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
):
    return load_current_user(session, auth.credentials)


def admin_required(current_user=Depends(get_current_user)):
    if _normalize_role(current_user.get("role")) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user

