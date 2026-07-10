"""Create alerts table.

Revision ID: 20260710_0013
Revises: 20260709_0012
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260710_0013"
down_revision: str | None = "20260709_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_id", sa.String(length=120), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("deduplication_key", sa.String(length=255), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by_user_id", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("severity IN ('Info', 'Warning', 'Critical')", name="ck_alerts_severity"),
        sa.CheckConstraint("status IN ('Active', 'Acknowledged', 'Resolved')", name="ck_alerts_status"),
        sa.ForeignKeyConstraint(["acknowledged_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_alerts_acknowledged_by_user_id", "alerts", ["acknowledged_by_user_id"])
    op.create_index("ix_alerts_category", "alerts", ["category"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])
    op.create_index("ix_alerts_first_seen_at", "alerts", ["first_seen_at"])
    op.create_index("ix_alerts_id", "alerts", ["id"])
    op.create_index("ix_alerts_last_seen_at", "alerts", ["last_seen_at"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_source_id", "alerts", ["source_id"])
    op.create_index("ix_alerts_source_type", "alerts", ["source_type"])
    op.create_index("ix_alerts_status", "alerts", ["status"])
    op.create_index(
        "uq_alerts_active_deduplication_key",
        "alerts",
        ["deduplication_key"],
        unique=True,
        postgresql_where=sa.text("status IN ('Active', 'Acknowledged')"),
        sqlite_where=sa.text("status IN ('Active', 'Acknowledged')"),
    )


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("uq_alerts_active_deduplication_key", table_name="alerts")
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_index("ix_alerts_source_type", table_name="alerts")
    op.drop_index("ix_alerts_source_id", table_name="alerts")
    op.drop_index("ix_alerts_severity", table_name="alerts")
    op.drop_index("ix_alerts_last_seen_at", table_name="alerts")
    op.drop_index("ix_alerts_id", table_name="alerts")
    op.drop_index("ix_alerts_first_seen_at", table_name="alerts")
    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_index("ix_alerts_category", table_name="alerts")
    op.drop_index("ix_alerts_acknowledged_by_user_id", table_name="alerts")
    op.drop_table("alerts")
