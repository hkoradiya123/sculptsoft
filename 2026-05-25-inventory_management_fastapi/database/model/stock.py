from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.dbhelper import Base

class Stock(Base):
    __tablename__ = "stock"

    stock_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("product.product_id"))
    inventory_id: Mapped[int | None] = mapped_column(ForeignKey("inventory.inventory_id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("location.location_id"))
    quantity: Mapped[int | None] = mapped_column()

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="stocks")
    inventory: Mapped["Inventory"] = relationship(back_populates="stocks")
    location: Mapped["Location"] = relationship(back_populates="stocks")

    # Composite Unique Constraint implementation
    __table_args__ = (
        UniqueConstraint("product_id", "inventory_id", "location_id", name="uq_stock_product_inventory_location"),
    )
