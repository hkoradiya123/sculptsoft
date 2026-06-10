from sqlalchemy import String, ForeignKey
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.dbhelper import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    area: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    locations = relationship(
        "Location",
        back_populates="inventory",
        cascade="all, delete-orphan"
    )

    stocks = relationship(
        "Stock",
        back_populates="inventory",
        cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "location"

    location_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    inventory_id: Mapped[int] = mapped_column(
        ForeignKey(
            "inventory.inventory_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    inventory = relationship(
        "Inventory",
        back_populates="locations"
    )

    stocks = relationship(
        "Stock",
        back_populates="location",
        cascade="all, delete-orphan"
    )
