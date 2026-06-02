import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from datetime import datetime



DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:Hkoradiya@localhost/fastapidb",
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def create_all_and_seed():
    """Create tables and seed default roles/permissions and an admin user if missing."""
    from passlib.context import CryptContext
    from sqlalchemy.orm import Session

    from app.db.models import Role, Permission, User

    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # seed roles and permissions
        role_names = ["admin", "seller", "user"]
        permission_map = {
            "admin": ["create_user", "delete_user", "view_dashboard", "manage_products"],
            "seller": ["manage_products", "view_dashboard"],
            "user": ["view_dashboard"],
        }

        for rn in role_names:
            if not db.query(Role).filter_by(name=rn).first():
                db.add(Role(name=rn))

        db.commit()

        # add permissions and link
        for rn, perms in permission_map.items():
            role = db.query(Role).filter_by(name=rn).first()
            for p in perms:
                perm = db.query(Permission).filter_by(name=p).first()
                if not perm:
                    perm = Permission(name=p)
                    db.add(perm)
                    db.commit()
                if perm not in role.permissions:
                    role.permissions.append(perm)
            db.add(role)

        db.commit()

        # create default admin user if missing
        if not db.query(User).filter_by(username="admin").first():
            admin = User(username="admin", password=pwd_ctx.hash("admin123"))
            admin.roles.append(db.query(Role).filter_by(name="admin").first())
            db.add(admin)
            db.commit()

    finally:
        db.close()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
