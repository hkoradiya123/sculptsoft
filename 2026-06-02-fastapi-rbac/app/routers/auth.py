from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from app.auth.dependencies import get_db
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.permissions.permissions import get_permissions, require_permissions
from app.db.models import User, RefreshToken

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if user is None or not pwd_ctx.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    roles = [r.name for r in user.roles]
    permissions = get_permissions(roles)

    access_token = create_access_token(username=user.username, roles=roles, permissions=permissions)

    # create refresh token and persist
    refresh_token_str, refresh_expires_iso = create_refresh_token()
    rt = RefreshToken(token=refresh_token_str, user_id=user.id, expires_at=refresh_expires_iso)
    db.add(rt)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "roles": roles,
        "permissions": permissions,
        "refresh_token": refresh_token_str,
    }


@router.post("/token/refresh")
def refresh_token(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not rt:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # check expiry
    try:
        expires_at = datetime.fromisoformat(rt.expires_at)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token data")

    if expires_at < datetime.now(timezone.utc):
        db.delete(rt)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.id == rt.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    roles = [r.name for r in user.roles]
    permissions = get_permissions(roles)
    access_token = create_access_token(username=user.username, roles=roles, permissions=permissions)

    # rotate: create new refresh token and delete old
    new_token, new_expires = create_refresh_token()
    new_rt = RefreshToken(token=new_token, user_id=user.id, expires_at=new_expires)
    db.add(new_rt)
    db.delete(rt)
    db.commit()

    return {"access_token": access_token, "refresh_token": new_token}


@router.get("/dashboard")
def dashboard(user=Depends(require_permissions("view_dashboard"))):
    return {
        "message": "dashboard",
        "user": user["sub"],
    }
