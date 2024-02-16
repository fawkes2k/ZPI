"""add table course_review

Revision ID: cc3d3cf79598
Revises: 40916f1fd11e
Create Date: 2024-02-16 12:50:31.594665

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'cc3d3cf79598'
down_revision = '40916f1fd11e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS course_review(
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    course_id UUID REFERENCES course(course_id) ON DELETE CASCADE NOT NULL,
    author UUID REFERENCES bc_user(user_id) ON DELETE CASCADE NOT NULL,
    rating INT2 NOT NULL DEFAULT 0 CHECK(rating > 0 AND rating < 6),
    comment TEXT NOT NULL UNIQUE DEFAULT 'DUMMY' CHECK(comment ~ '^.{1,2000}$'),
    UNIQUE(course_id, author));""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS course_review;")
