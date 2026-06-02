import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base, User


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:Hkoradiya@localhost/fastapidb",
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_default_users() -> None:
    """Seed a minimal user set for demo auth if missing."""
    Base.metadata.create_all(bind=engine)

    defaults = [
        ("admin", "admin", "admin123"),
        ("admin2", "admin", "admin123"),
        ("manager1", "manager", "manager123"),
        ("manager2", "manager", "manager123"),
        ("manager3", "manager", "manager123"),
        ("employee1", "employee", "employee123"),
        ("employee2", "employee", "employee123"),
        ("employee3", "employee", "employee123"),
        ("employee4", "employee", "employee123"),
        ("employee5", "employee", "employee123"),
        ("qa1", "employee", "employee123"),
        ("intern1", "employee", "employee123"),
    ]

    with SessionLocal() as db:
        for username, role, password in defaults:
            exists = db.query(User).filter(User.username == username).first()
            if exists is None:
                db.add(User(username=username, password=password, role=role))
        db.commit()
