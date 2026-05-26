from sqlalchemy import String, ForeignKey
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.dbhelper import Base

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    area: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))

    # Relationships
    locations: Mapped[List["Location"]] = relationship(back_populates="inventory", cascade="all, delete-orphan")
    stocks: Mapped[List["Stock"]] = relationship(back_populates="inventory")


class Location(Base):
    __tablename__ = "location"

    location_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.inventory_id", ondelete="CASCADE"), nullable=False)
    address: Mapped[str | None] = mapped_column(String(150))

    # Relationships
    inventory: Mapped["Inventory"] = relationship(back_populates="locations")
    stocks: Mapped[List["Stock"]] = relationship(back_populates="location")
