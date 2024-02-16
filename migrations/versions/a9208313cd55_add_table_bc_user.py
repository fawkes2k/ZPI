"""add table bc_user

Revision ID: a9208313cd55
Revises: 
Create Date: 2024-02-16 12:50:00.676777

"""
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a9208313cd55'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS bc_user(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    last_name TEXT NOT NULL DEFAULT 'Doe' CHECK(last_name ~ '^.{1,100}$'),
    first_name TEXT NOT NULL DEFAULT 'John' CHECK(first_name ~ '^.{1,100}$'),
    email TEXT NOT NULL DEFAULT 'ZPI@example.com' CHECK(email ~ '^.{1,100}$'),
    hashed_password TEXT UNIQUE NOT NULL CHECK(hashed_password ~ '^[0-9a-f]{128}$'),
    salt BYTEA UNIQUE NOT NULL CHECK(length(salt) > 0));""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS bc_user;")
