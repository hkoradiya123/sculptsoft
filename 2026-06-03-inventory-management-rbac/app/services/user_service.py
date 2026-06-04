from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password, verify_password


def change_user_password(
    session: Session, 
    user_id: int, 
    old_password: str, 
    new_password: str
) -> None:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
    
    user.hashed_password = hash_password(new_password)
    session.commit()


def admin_reset_password(
    session: Session, 
    user_id: int, 
    new_password: str
) -> None:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.hashed_password = hash_password(new_password)
    session.commit()
