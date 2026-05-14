from sqlalchemy.orm import Session

from app.repositories import user_repository
from app.schemas.user_schema import UserCreate


def create_user(db: Session, user_data: UserCreate):
    return user_repository.create_user(db, user_data)


def list_users(db: Session):
    return user_repository.get_users(db)


def get_user(db: Session, user_id: int):
    return user_repository.get_user_by_id(db, user_id)
