from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.jwt_auth import get_current_user
from app.auth.jwt_auth import hash_password
from app.db.models import User
from app.db.session import get_db
import json
from pathlib import Path



router = APIRouter(prefix="/api/v1", tags=["users"])


class SignupRequest(BaseModel):
    username: str
    password: str
    role: str = "employee"


@router.get("/users", dependencies=[Depends(get_current_user)])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return {
        "users": [
            {"id": user.id, "username": user.username, "role": user.role}
            for user in users
        ]
    }
    
@router.get("/all-users", dependencies=[Depends(get_current_user)])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return {
        "users": [
            {"id": user.id, "username": user.username, "role": user.role}
            for user in users
        ]
    }


@router.post("/users", dependencies=[Depends(get_current_user)])
async def create_user(username: str , password:str , role:str, db: Session = Depends(get_db)): 
    created = User(username=username, password=hash_password(password), role=role)
    db.add(created)
    db.commit()
    db.refresh(created)
    return {"message": "user created", "id": created.id}


@router.put("/users/{id}", dependencies=[Depends(get_current_user)])
async def update_user(id: int, username: str , role: str = None, password: str = None, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "user not found"}
    if username is not None:
        user.username = username
    if role is not None:
        user.role = role
    if password is not None:
        user.password = hash_password(password)
    db.commit()
    db.refresh(user)
    return {"message": f"user {id} updated"}


@router.delete("/users/{id}", dependencies=[Depends(get_current_user)])
async def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        return {"message": "user not found"}
    db.delete(user)
    db.commit()
    return {"message": f"user {id} deleted"}
