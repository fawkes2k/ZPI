"""add table attachment

Revision ID: d12e085e9198
Revises: ad1121ef971f
Create Date: 2024-02-16 12:50:55.133379

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'd12e085e9198'
down_revision = 'ad1121ef971f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS attachment(
    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creation_date TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
    file_name TEXT NOT NULL UNIQUE DEFAULT 'ZZDUMMY.BIN' CHECK(file_name ~ '^.{1,255}$'),
    file_hash TEXT NOT NULL UNIQUE CHECK(file_hash ~ '^[0-9a-f]{128}$'),
    video_id UUID REFERENCES video(video_id) ON DELETE CASCADE NOT NULL,
    file_size BIGINT NOT NULL DEFAULT 1024 CHECK(file_size > 0));""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS attachment;")
