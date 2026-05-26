from typing import Generator

from sqlalchemy.orm import Session

from database.dbhelper import db
from api.deps.auth import admin_required, get_current_user

__all__ = ["get_db", "get_current_user", "admin_required"]

def get_db() -> Generator[Session, None, None]:
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
