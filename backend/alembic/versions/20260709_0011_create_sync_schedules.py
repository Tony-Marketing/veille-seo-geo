"""Create synchronization schedules table.

Revision ID: 20260709_0011
Revises: 20260708_0010
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260709_0011"
down_revision: str | None = "20260708_0010"
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
        "sync_schedules",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sync_type", sa.String(length=30), nullable=False),
        sa.Column("frequency", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("target_id", sa.String(length=120), nullable=True),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_status", sa.String(length=30), nullable=True),
        sa.Column("last_run_message", sa.Text(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(length=80), nullable=False, server_default="Europe/Paris"),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_sync_schedules_created_by_user_id", "sync_schedules", ["created_by_user_id"])
    op.create_index("ix_sync_schedules_frequency", "sync_schedules", ["frequency"])
    op.create_index("ix_sync_schedules_id", "sync_schedules", ["id"])
    op.create_index("ix_sync_schedules_is_active", "sync_schedules", ["is_active"])
    op.create_index("ix_sync_schedules_last_run_at", "sync_schedules", ["last_run_at"])
    op.create_index("ix_sync_schedules_last_run_status", "sync_schedules", ["last_run_status"])
    op.create_index("ix_sync_schedules_name", "sync_schedules", ["name"])
    op.create_index("ix_sync_schedules_next_run_at", "sync_schedules", ["next_run_at"])
    op.create_index("ix_sync_schedules_status", "sync_schedules", ["status"])
    op.create_index("ix_sync_schedules_sync_type", "sync_schedules", ["sync_type"])
    op.create_index("ix_sync_schedules_target_id", "sync_schedules", ["target_id"])
    op.create_index("ix_sync_schedules_target_type", "sync_schedules", ["target_type"])
    op.create_index("ix_sync_schedules_updated_by_user_id", "sync_schedules", ["updated_by_user_id"])
    op.create_index("ix_sync_schedules_website_id", "sync_schedules", ["website_id"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_sync_schedules_website_id", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_updated_by_user_id", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_target_type", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_target_id", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_sync_type", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_status", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_next_run_at", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_name", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_last_run_status", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_last_run_at", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_is_active", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_id", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_frequency", table_name="sync_schedules")
    op.drop_index("ix_sync_schedules_created_by_user_id", table_name="sync_schedules")
    op.drop_table("sync_schedules")

