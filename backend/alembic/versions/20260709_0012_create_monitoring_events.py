"""Create monitoring events table.

Revision ID: 20260709_0012
Revises: 20260709_0011
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260709_0012"
down_revision: str | None = "20260709_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""

    op.create_table(
        "monitoring_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_monitoring_events_created_at", "monitoring_events", ["created_at"])
    op.create_index("ix_monitoring_events_event_type", "monitoring_events", ["event_type"])
    op.create_index("ix_monitoring_events_severity", "monitoring_events", ["severity"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_monitoring_events_severity", table_name="monitoring_events")
    op.drop_index("ix_monitoring_events_event_type", table_name="monitoring_events")
    op.drop_index("ix_monitoring_events_created_at", table_name="monitoring_events")
    op.drop_table("monitoring_events")
