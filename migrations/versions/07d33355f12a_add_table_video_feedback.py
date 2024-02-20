"""add table video_feedback

Revision ID: 07d33355f12a
Revises: d12e085e9198
Create Date: 2024-02-16 12:51:07.334696

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '07d33355f12a'
down_revision = 'd12e085e9198'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS video_feedback(
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    video_id UUID REFERENCES video(video_id) ON DELETE CASCADE NOT NULL,
    author UUID REFERENCES bc_user(user_id) ON DELETE CASCADE NOT NULL,
    comment TEXT NOT NULL UNIQUE DEFAULT 'DUMMY');""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS video_feedback;")
