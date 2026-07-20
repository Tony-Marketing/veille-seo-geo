"""Create GEO visibility snapshots table.

Revision ID: 20260720_0016
Revises: 20260720_0015
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260720_0016"
down_revision: str | None = "20260720_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""

    op.create_table(
        "geo_visibility_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("prompt", sa.String(length=500), nullable=False),
        sa.Column("entity", sa.String(length=255), nullable=False),
        sa.Column("visibility_score", sa.Float(), nullable=False),
        sa.Column("citation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ranking", sa.Integer(), nullable=True),
        sa.Column("answer_hash", sa.String(length=64), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "visibility_score >= 0 AND visibility_score <= 100",
            name="ck_geo_visibility_snapshots_score",
        ),
        sa.CheckConstraint("citation_count >= 0", name="ck_geo_visibility_snapshots_citations"),
        sa.CheckConstraint("source_count >= 0", name="ck_geo_visibility_snapshots_sources"),
        sa.CheckConstraint("ranking IS NULL OR ranking > 0", name="ck_geo_visibility_snapshots_ranking"),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "website_id",
            "provider",
            "prompt",
            "entity",
            "answer_hash",
            "captured_at",
            name="uq_geo_visibility_snapshots_observation",
        ),
    )
    op.create_index("ix_geo_visibility_snapshots_answer_hash", "geo_visibility_snapshots", ["answer_hash"])
    op.create_index("ix_geo_visibility_snapshots_captured_at", "geo_visibility_snapshots", ["captured_at"])
    op.create_index("ix_geo_visibility_snapshots_entity", "geo_visibility_snapshots", ["entity"])
    op.create_index("ix_geo_visibility_snapshots_id", "geo_visibility_snapshots", ["id"])
    op.create_index("ix_geo_visibility_snapshots_prompt", "geo_visibility_snapshots", ["prompt"])
    op.create_index("ix_geo_visibility_snapshots_provider", "geo_visibility_snapshots", ["provider"])
    op.create_index(
        "ix_geo_visibility_snapshots_scope",
        "geo_visibility_snapshots",
        ["website_id", "provider", "entity"],
    )
    op.create_index(
        "ix_geo_visibility_snapshots_visibility_score",
        "geo_visibility_snapshots",
        ["visibility_score"],
    )
    op.create_index("ix_geo_visibility_snapshots_website_id", "geo_visibility_snapshots", ["website_id"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_geo_visibility_snapshots_website_id", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_visibility_score", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_scope", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_provider", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_prompt", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_id", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_entity", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_captured_at", table_name="geo_visibility_snapshots")
    op.drop_index("ix_geo_visibility_snapshots_answer_hash", table_name="geo_visibility_snapshots")
    op.drop_table("geo_visibility_snapshots")
