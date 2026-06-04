"""ensure users.password column exists

Revision ID: 0003_password
Revises: 0002_add_role_column_if_missing
Create Date: 2026-06-02
"""

from alembic import op


revision = "0003_password"
down_revision = "0002_add_role_column_if_missing"
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
                WHERE table_name = 'users' AND column_name = 'password'
            ) THEN
                ALTER TABLE users ADD COLUMN password VARCHAR(255);
            END IF;
        END
        $$;
        """
    )
    op.execute("UPDATE users SET password = COALESCE(password, 'employee123')")
    op.execute("ALTER TABLE users ALTER COLUMN password SET NOT NULL")


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'password'
            ) THEN
                ALTER TABLE users DROP COLUMN password;
            END IF;
        END
        $$;
        """
    )
