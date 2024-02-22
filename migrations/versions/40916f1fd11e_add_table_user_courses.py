"""add table user_courses

Revision ID: 40916f1fd11e
Revises: 84c08b828cf0
Create Date: 2024-02-16 12:50:23.247438

"""
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '40916f1fd11e'
down_revision = '84c08b828cf0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS user_courses(
    user_id UUID REFERENCES bc_user(user_id) ON DELETE CASCADE NOT NULL,
    course_id UUID REFERENCES course(course_id) ON DELETE CASCADE NOT NULL,
    UNIQUE(user_id, course_id));""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_courses;")
