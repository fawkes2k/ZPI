"""add table course

Revision ID: 84c08b828cf0
Revises: a9208313cd55
Create Date: 2024-02-16 12:50:10.376528

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '84c08b828cf0'
down_revision = 'a9208313cd55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS course(
    course_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    course_name TEXT UNIQUE NOT NULL DEFAULT 'DUMMY' CHECK(course_name ~ '^.{1,100}$'),
    description TEXT UNIQUE NOT NULL DEFAULT 'DUMMY',
    price NUMERIC(5,2) NOT NULL DEFAULT 100 CHECK(price >= 0),
    image TEXT UNIQUE NOT NULL CHECK(length(image) > 0),
    author UUID REFERENCES bc_user(user_id) ON DELETE CASCADE NOT NULL);""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS course;")
