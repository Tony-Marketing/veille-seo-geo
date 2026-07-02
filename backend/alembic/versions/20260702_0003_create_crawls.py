"""Create crawl sessions and pages.

Revision ID: 20260702_0003
Revises: 20260626_0002
Create Date: 2026-07-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260702_0003"
down_revision: str | None = "20260626_0002"
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
        "crawl_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("start_url", sa.String(length=500), nullable=False),
        sa.Column("normalized_start_url", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("max_depth", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("max_pages", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("pages_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pages_crawled", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pages_failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pending_urls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_depth_reached", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_progress_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_crawl_sessions_id", "crawl_sessions", ["id"])
    op.create_index("ix_crawl_sessions_normalized_start_url", "crawl_sessions", ["normalized_start_url"])
    op.create_index("ix_crawl_sessions_status", "crawl_sessions", ["status"])
    op.create_index("ix_crawl_sessions_website_id", "crawl_sessions", ["website_id"])

    op.create_table(
        "crawl_pages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("crawl_session_id", sa.Integer(), nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("normalized_url", sa.String(length=1000), nullable=False),
        sa.Column("final_url", sa.String(length=1000), nullable=True),
        sa.Column("final_normalized_url", sa.String(length=1000), nullable=True),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("is_redirect", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("redirect_url", sa.String(length=1000), nullable=True),
        sa.Column("redirect_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("visited_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_session_id"], ["crawl_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("crawl_session_id", "normalized_url", name="uq_crawl_pages_session_normalized_url"),
    )
    op.create_index("ix_crawl_pages_crawl_session_id", "crawl_pages", ["crawl_session_id"])
    op.create_index("ix_crawl_pages_depth", "crawl_pages", ["depth"])
    op.create_index("ix_crawl_pages_final_normalized_url", "crawl_pages", ["final_normalized_url"])
    op.create_index("ix_crawl_pages_id", "crawl_pages", ["id"])
    op.create_index("ix_crawl_pages_normalized_url", "crawl_pages", ["normalized_url"])
    op.create_index("ix_crawl_pages_status_code", "crawl_pages", ["status_code"])
    op.create_index("ix_crawl_pages_website_id", "crawl_pages", ["website_id"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_crawl_pages_website_id", table_name="crawl_pages")
    op.drop_index("ix_crawl_pages_status_code", table_name="crawl_pages")
    op.drop_index("ix_crawl_pages_normalized_url", table_name="crawl_pages")
    op.drop_index("ix_crawl_pages_id", table_name="crawl_pages")
    op.drop_index("ix_crawl_pages_final_normalized_url", table_name="crawl_pages")
    op.drop_index("ix_crawl_pages_depth", table_name="crawl_pages")
    op.drop_index("ix_crawl_pages_crawl_session_id", table_name="crawl_pages")
    op.drop_table("crawl_pages")

    op.drop_index("ix_crawl_sessions_website_id", table_name="crawl_sessions")
    op.drop_index("ix_crawl_sessions_status", table_name="crawl_sessions")
    op.drop_index("ix_crawl_sessions_normalized_start_url", table_name="crawl_sessions")
    op.drop_index("ix_crawl_sessions_id", table_name="crawl_sessions")
    op.drop_table("crawl_sessions")

