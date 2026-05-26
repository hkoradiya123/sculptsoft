from typing import Generator

from sqlalchemy.orm import Session

from database.dbhelper import db


def get_db() -> Generator[Session, None, None]:
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
