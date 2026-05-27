import enum

from sqlalchemy import Column, Enum, Integer, String

from .db import Base


class Sex(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
