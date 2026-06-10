"""inventory improvements

Revision ID: 8166579b9252
Revises:
Create Date: 2026-06-03 16:40:04.040719

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "8166579b9252"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ==========================
    # INVENTORY
    # ==========================

    op.create_table(
        "inventory",
        sa.Column("inventory_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("area", sa.String(length=100), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
    )

    op.create_index(
        "idx_inventory_city",
        "inventory",
        ["city"],
    )

    # ==========================
    # PRODUCT
    # ==========================

    op.create_table(
        "product",
        sa.Column("product_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column(
            "price",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "price >= 0",
            name="ck_product_price_positive",
        ),
    )

    # ==========================
    # PRICE HISTORY
    # ==========================

    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey(
                "product.product_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.Column(
            "changed_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "price >= 0",
            name="ck_history_price_positive",
        ),
    )

    op.create_index(
        "idx_price_history_product",
        "price_history",
        ["product_id"],
    )

    # ==========================
    # LOCATION
    # ==========================

    op.create_table(
        "location",
        sa.Column("location_id", sa.Integer(), primary_key=True),
        sa.Column(
            "inventory_id",
            sa.Integer(),
            sa.ForeignKey(
                "inventory.inventory_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "address",
            sa.String(length=150),
            nullable=False,
        ),
    )

    # ==========================
    # STOCK
    # ==========================

    op.create_table(
        "stock",
        sa.Column("stock_id", sa.Integer(), primary_key=True),

        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey(
                "product.product_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "inventory_id",
            sa.Integer(),
            sa.ForeignKey(
                "inventory.inventory_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "location_id",
            sa.Integer(),
            sa.ForeignKey(
                "location.location_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.CheckConstraint(
            "quantity >= 0",
            name="ck_stock_quantity_positive",
        ),

        sa.UniqueConstraint(
            "product_id",
            "inventory_id",
            "location_id",
            name="uq_stock_product_inventory_location",
        ),
    )

    op.create_index(
        "idx_stock_product",
        "stock",
        ["product_id"],
    )

    op.create_index(
        "idx_stock_inventory",
        "stock",
        ["inventory_id"],
    )

    op.create_index(
        "idx_stock_location",
        "stock",
        ["location_id"],
    )

    # ==========================
    # USERS
    # ==========================

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False,
            server_default="user",
        ),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
    )

    # ==========================
    # PRICE HISTORY TRIGGER
    # ==========================

    op.execute(
        """
        CREATE OR REPLACE FUNCTION log_price_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.price IS DISTINCT FROM NEW.price THEN
                INSERT INTO price_history(product_id, price)
                VALUES (NEW.product_id, NEW.price);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_product_price_update
        AFTER UPDATE ON product
        FOR EACH ROW
        EXECUTE FUNCTION log_price_change();
        """
    )

    # ==========================
    # INITIAL PRICE TRIGGER
    # ==========================

    op.execute(
        """
        CREATE OR REPLACE FUNCTION log_initial_price()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO price_history(product_id, price)
            VALUES (NEW.product_id, NEW.price);

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_product_price_insert
        AFTER INSERT ON product
        FOR EACH ROW
        EXECUTE FUNCTION log_initial_price();
        """
    )


def downgrade() -> None:

    op.execute(
        "DROP TRIGGER IF EXISTS trg_product_price_update ON product;"
    )

    op.execute(
        "DROP TRIGGER IF EXISTS trg_product_price_insert ON product;"
    )

    op.execute(
        "DROP FUNCTION IF EXISTS log_price_change();"
    )

    op.execute(
        "DROP FUNCTION IF EXISTS log_initial_price();"
    )

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("idx_stock_location", table_name="stock")
    op.drop_index("idx_stock_inventory", table_name="stock")
    op.drop_index("idx_stock_product", table_name="stock")
    op.drop_table("stock")

    op.drop_table("location")

    op.drop_index(
        "idx_price_history_product",
        table_name="price_history",
    )
    op.drop_table("price_history")

    op.drop_table("product")

    op.drop_index(
        "idx_inventory_city",
        table_name="inventory",
    )
    op.drop_table("inventory")