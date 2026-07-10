"""Create orchestration processing tables.

Revision ID: 20260710_0014
Revises: 20260710_0013
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260710_0014"
down_revision: str | None = "20260710_0013"
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
        "processing_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("worker_id", sa.String(length=120), nullable=True),
        sa.Column("lock_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("monitoring_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["monitoring_event_id"], ["monitoring_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["schedule_id"], ["sync_schedules.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_processing_jobs_available_at", "processing_jobs", ["available_at"])
    op.create_index("ix_processing_jobs_created_at", "processing_jobs", ["created_at"])
    op.create_index("ix_processing_jobs_failed_at", "processing_jobs", ["failed_at"])
    op.create_index("ix_processing_jobs_finished_at", "processing_jobs", ["finished_at"])
    op.create_index("ix_processing_jobs_id", "processing_jobs", ["id"])
    op.create_index("ix_processing_jobs_idempotency_key", "processing_jobs", ["idempotency_key"], unique=True)
    op.create_index("ix_processing_jobs_job_type", "processing_jobs", ["job_type"])
    op.create_index("ix_processing_jobs_job_type_status", "processing_jobs", ["job_type", "status"])
    op.create_index("ix_processing_jobs_lock_expires_at", "processing_jobs", ["lock_expires_at"])
    op.create_index("ix_processing_jobs_monitoring_event_id", "processing_jobs", ["monitoring_event_id"])
    op.create_index("ix_processing_jobs_reserved_at", "processing_jobs", ["reserved_at"])
    op.create_index("ix_processing_jobs_schedule_id", "processing_jobs", ["schedule_id"])
    op.create_index("ix_processing_jobs_started_at", "processing_jobs", ["started_at"])
    op.create_index("ix_processing_jobs_status", "processing_jobs", ["status"])
    op.create_index("ix_processing_jobs_status_available_at", "processing_jobs", ["status", "available_at"])
    op.create_index("ix_processing_jobs_worker_id", "processing_jobs", ["worker_id"])

    op.create_table(
        "processing_job_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("event", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("context", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["processing_jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_processing_job_logs_created_at", "processing_job_logs", ["created_at"])
    op.create_index("ix_processing_job_logs_event", "processing_job_logs", ["event"])
    op.create_index("ix_processing_job_logs_id", "processing_job_logs", ["id"])
    op.create_index("ix_processing_job_logs_job_id", "processing_job_logs", ["job_id"])
    op.create_index("ix_processing_job_logs_level", "processing_job_logs", ["level"])

    op.create_table(
        "processing_workers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("worker_id", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_job_id", sa.Integer(), nullable=True),
        sa.Column("version", sa.String(length=80), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["current_job_id"], ["processing_jobs.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_processing_workers_current_job_id", "processing_workers", ["current_job_id"])
    op.create_index("ix_processing_workers_id", "processing_workers", ["id"])
    op.create_index("ix_processing_workers_last_heartbeat_at", "processing_workers", ["last_heartbeat_at"])
    op.create_index("ix_processing_workers_status", "processing_workers", ["status"])
    op.create_index("ix_processing_workers_worker_id", "processing_workers", ["worker_id"], unique=True)


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_processing_workers_worker_id", table_name="processing_workers")
    op.drop_index("ix_processing_workers_status", table_name="processing_workers")
    op.drop_index("ix_processing_workers_last_heartbeat_at", table_name="processing_workers")
    op.drop_index("ix_processing_workers_id", table_name="processing_workers")
    op.drop_index("ix_processing_workers_current_job_id", table_name="processing_workers")
    op.drop_table("processing_workers")

    op.drop_index("ix_processing_job_logs_level", table_name="processing_job_logs")
    op.drop_index("ix_processing_job_logs_job_id", table_name="processing_job_logs")
    op.drop_index("ix_processing_job_logs_id", table_name="processing_job_logs")
    op.drop_index("ix_processing_job_logs_event", table_name="processing_job_logs")
    op.drop_index("ix_processing_job_logs_created_at", table_name="processing_job_logs")
    op.drop_table("processing_job_logs")

    op.drop_index("ix_processing_jobs_worker_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_status_available_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_status", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_started_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_schedule_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_reserved_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_monitoring_event_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_lock_expires_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_job_type_status", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_job_type", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_idempotency_key", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_finished_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_failed_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_created_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_available_at", table_name="processing_jobs")
    op.drop_table("processing_jobs")
