"""Create websites tables.

Revision ID: 20260626_0002
Revises: 20260626_0001
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260626_0002"
down_revision: str | None = "20260626_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def upgrade() -> None:
    """Apply migration."""

    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
        sa.UniqueConstraint("name", name="uq_entities_name"),
    )
    op.create_index("ix_entities_name", "entities", ["name"], unique=True)

    op.create_table(
        "websites",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("cms", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("url", name="uq_websites_url"),
    )
    op.create_index("ix_websites_url", "websites", ["url"], unique=True)


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_websites_url", table_name="websites")
    op.drop_table("websites")

    op.drop_index("ix_entities_name", table_name="entities")
    op.drop_table("entities")
