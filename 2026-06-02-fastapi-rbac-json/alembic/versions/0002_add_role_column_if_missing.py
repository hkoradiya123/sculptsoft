"""ensure users.role column exists

Revision ID: 0002_add_role_column_if_missing
Revises: 0001_initial
Create Date: 2026-06-02
"""

from alembic import op


revision = "0002_add_role_column_if_missing"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            ) THEN
                ALTER TABLE users ADD COLUMN role VARCHAR(30);
            END IF;
        END
        $$;
        """
    )
    op.execute("UPDATE users SET role = COALESCE(role, 'employee')")
    op.execute("ALTER TABLE users ALTER COLUMN role SET NOT NULL")


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            ) THEN
                ALTER TABLE users DROP COLUMN role;
            END IF;
        END
        $$;
        """
    )
