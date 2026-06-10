from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.dbhelper import Base

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.dbhelper import Base


class Stock(Base):
    __tablename__ = "stock"

    stock_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "product.product_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    inventory_id: Mapped[int] = mapped_column(
        ForeignKey(
            "inventory.inventory_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey(
            "location.location_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=0
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "inventory_id",
            "location_id",
            name="uq_stock_product_inventory_location"
        ),
        CheckConstraint(
            "quantity >= 0",
            name="ck_stock_quantity_positive"
        ),
    )

    product = relationship(
        "Product",
        back_populates="stocks"
    )

    inventory = relationship(
        "Inventory",
        back_populates="stocks"
    )

    location = relationship(
        "Location",
        back_populates="stocks"
    )

