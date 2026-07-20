"""Create transverse recommendations table.

Revision ID: 20260720_0015
Revises: 20260710_0014
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260720_0015"
down_revision: str | None = "20260710_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("impact", sa.String(length=30), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("deduplication_key", sa.String(length=255), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')",
            name="ck_recommendations_priority",
        ),
        sa.CheckConstraint(
            "status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'IGNORED')",
            name="ck_recommendations_status",
        ),
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('EASY', 'MEDIUM', 'HARD')",
            name="ck_recommendations_difficulty",
        ),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_recommendations_category", "recommendations", ["category"])
    op.create_index("ix_recommendations_created_at", "recommendations", ["created_at"])
    op.create_index("ix_recommendations_difficulty", "recommendations", ["difficulty"])
    op.create_index("ix_recommendations_id", "recommendations", ["id"])
    op.create_index("ix_recommendations_impact", "recommendations", ["impact"])
    op.create_index("ix_recommendations_priority", "recommendations", ["priority"])
    op.create_index("ix_recommendations_score", "recommendations", ["score"])
    op.create_index("ix_recommendations_source", "recommendations", ["source"])
    op.create_index("ix_recommendations_source_id", "recommendations", ["source_id"])
    op.create_index("ix_recommendations_status", "recommendations", ["status"])
    op.create_index("ix_recommendations_website_id", "recommendations", ["website_id"])
    op.create_index(
        "uq_recommendations_deduplication_key",
        "recommendations",
        ["deduplication_key"],
        unique=True,
    )


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("uq_recommendations_deduplication_key", table_name="recommendations")
    op.drop_index("ix_recommendations_website_id", table_name="recommendations")
    op.drop_index("ix_recommendations_status", table_name="recommendations")
    op.drop_index("ix_recommendations_source_id", table_name="recommendations")
    op.drop_index("ix_recommendations_source", table_name="recommendations")
    op.drop_index("ix_recommendations_score", table_name="recommendations")
    op.drop_index("ix_recommendations_priority", table_name="recommendations")
    op.drop_index("ix_recommendations_impact", table_name="recommendations")
    op.drop_index("ix_recommendations_id", table_name="recommendations")
    op.drop_index("ix_recommendations_difficulty", table_name="recommendations")
    op.drop_index("ix_recommendations_created_at", table_name="recommendations")
    op.drop_index("ix_recommendations_category", table_name="recommendations")
    op.drop_table("recommendations")
