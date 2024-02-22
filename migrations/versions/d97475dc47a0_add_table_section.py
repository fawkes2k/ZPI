"""add table section

Revision ID: d97475dc47a0
Revises: cc3d3cf79598
Create Date: 2024-02-16 12:50:40.659920

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd97475dc47a0'
down_revision = 'cc3d3cf79598'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS section(
    section_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    section_name TEXT NOT NULL UNIQUE DEFAULT 'DUMMY' CHECK(section_name ~ '^.{1,100}$'),
    course_id UUID REFERENCES course(course_id) ON DELETE CASCADE NOT NULL);""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS section;")
