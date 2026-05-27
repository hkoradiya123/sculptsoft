import os
from contextlib import contextmanager
from pathlib import Path

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
dotenv.load_dotenv(PROJECT_ROOT / ".env")


class Base(DeclarativeBase):
    pass


def get_database_url():
    database_url = os.getenv("DATABASE_URL") or os.getenv("database_url")
    if database_url:
        return database_url

    host = os.getenv("host", "localhost")
    user = os.getenv("user", "postgres")
    password = os.getenv("password", "")
    database = os.getenv("database", "userdb")
    port = os.getenv("port")
    port_suffix = f":{port}" if port else ""
    return f"postgresql://{user}:{password}@{host}{port_suffix}/{database}"


class DBHelper:
    def __init__(self, database_url=None):
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url, echo=False)
        self.Session = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )

    def get_session(self):
        return self.Session()

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self):
        Base.metadata.create_all(self.engine)


db = DBHelper()

