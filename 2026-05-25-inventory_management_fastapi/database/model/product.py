from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import String, Numeric, ForeignKey, DateTime, func, DDL, event
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.dbhelper import Base

class Product(Base):
    __tablename__ = "product"

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(100))
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Relationships
    price_histories: Mapped[List["PriceHistory"]] = relationship(back_populates="product")
    stocks: Mapped[List["Stock"]] = relationship(back_populates="product")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("product.product_id"))
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="price_histories")


# --- Native PostgreSQL Trigger Definition ---
trigger_function_ddl = DDL("""
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.price IS DISTINCT FROM NEW.price THEN
        INSERT INTO price_history (product_id, price)
        VALUES (NEW.product_id, NEW.price);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")

trigger_binding_ddl = DDL("""
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'after_price_update'
    ) THEN
        CREATE TRIGGER after_price_update
        AFTER UPDATE ON product
        FOR EACH ROW
        EXECUTE FUNCTION log_price_change();
    END IF;
END;
$$;
""")

# Bind DDL components to the Product metadata lifecycle
event.listen(Product.__table__, 'after_create', trigger_function_ddl.execute_if(dialect='postgresql'))
event.listen(Product.__table__, 'after_create', trigger_binding_ddl.execute_if(dialect='postgresql'))
