"""create kb pages and chunks

Revision ID: e7b3d5a91c26
Revises: c4a1e8b27d09
Create Date: 2026-10-11 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import pgvector.sqlalchemy
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7b3d5a91c26"
down_revision: Union[str, Sequence[str], None] = "c4a1e8b27d09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "kb_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url", name="uq_kb_pages_url"),
    )
    op.create_table(
        "kb_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("page_id", sa.Integer(), nullable=False),
        sa.Column("chunk_number", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=3072), nullable=True),
        sa.ForeignKeyConstraint(
            ["page_id"],
            ["kb_pages.id"],
            name="fk_kb_chunks_page_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "page_id",
            "chunk_number",
            name="uq_kb_chunks_page_id_chunk_number",
        ),
    )
    op.create_index("ix_kb_chunks_page_id", "kb_chunks", ["page_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_kb_chunks_page_id", table_name="kb_chunks")
    op.drop_table("kb_chunks")
    op.drop_table("kb_pages")
