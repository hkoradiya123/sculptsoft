from typing import AsyncGenerator

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./app.db"


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_data() -> None:
    from .models import Person, Sex

    async with async_session() as session:
        existing = await session.execute(select(func.count()).select_from(Person))
        if existing.scalar_one() > 0:
            return

        session.add_all(
            [
                Person(name="Alice", country="USA", age=28, sex=Sex.FEMALE),
                Person(name="Bruno", country="Brazil", age=35, sex=Sex.MALE),
                Person(name="Chen", country="China", age=41, sex=Sex.MALE),
                Person(name="Dewi", country="Indonesia", age=23, sex=Sex.FEMALE),
                Person(name="Elena", country="Spain", age=31, sex=Sex.FEMALE),
                Person(name="Farid", country="UAE", age=29, sex=Sex.MALE),
                Person(name="Grace", country="UK", age=37, sex=Sex.FEMALE),
                Person(name="Hiro", country="Japan", age=33, sex=Sex.MALE),
                Person(name="Ines", country="Portugal", age=26, sex=Sex.FEMALE),
                Person(name="Jamal", country="Nigeria", age=39, sex=Sex.MALE),
                Person(name="Klara", country="Germany", age=27, sex=Sex.FEMALE),
            ]
        )
        await session.commit()
