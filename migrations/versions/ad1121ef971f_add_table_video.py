"""add table video

Revision ID: ad1121ef971f
Revises: d97475dc47a0
Create Date: 2024-02-16 12:50:48.562017

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ad1121ef971f'
down_revision = 'd97475dc47a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS video(
    video_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    video_name TEXT NOT NULL UNIQUE DEFAULT 'ZZDUMMY.MOV' CHECK(video_name ~ '^.{1,256}$'),
    section_id UUID REFERENCES section(section_id) ON DELETE CASCADE NOT NULL,
    video_hash TEXT NOT NULL UNIQUE CHECK(video_hash ~ '^[0-9a-f]{128}$'),
    length TIME NOT NULL CHECK(length > 0));""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS video;")
