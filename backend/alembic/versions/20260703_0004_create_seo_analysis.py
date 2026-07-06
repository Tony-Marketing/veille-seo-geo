"""Create SEO analysis tables.

Revision ID: 20260703_0004
Revises: 20260702_0003
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260703_0004"
down_revision: str | None = "20260702_0003"
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
        "seo_analyses",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("crawl_session_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("global_score", sa.Float(), nullable=True),
        sa.Column("pages_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pages_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("issues_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_session_id"], ["crawl_sessions.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_seo_analyses_crawl_session_id", "seo_analyses", ["crawl_session_id"])
    op.create_index("ix_seo_analyses_id", "seo_analyses", ["id"])
    op.create_index("ix_seo_analyses_status", "seo_analyses", ["status"])

    op.create_table(
        "seo_page_analyses",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("seo_analysis_id", sa.Integer(), nullable=False),
        sa.Column("crawl_page_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("issues_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_page_id"], ["crawl_pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seo_analysis_id"], ["seo_analyses.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("seo_analysis_id", "crawl_page_id", name="uq_seo_page_analyses_analysis_page"),
    )
    op.create_index("ix_seo_page_analyses_crawl_page_id", "seo_page_analyses", ["crawl_page_id"])
    op.create_index("ix_seo_page_analyses_id", "seo_page_analyses", ["id"])
    op.create_index("ix_seo_page_analyses_seo_analysis_id", "seo_page_analyses", ["seo_analysis_id"])
    op.create_index("ix_seo_page_analyses_status", "seo_page_analyses", ["status"])

    op.create_table(
        "seo_analysis_issues",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("seo_analysis_id", sa.Integer(), nullable=False),
        sa.Column("seo_page_analysis_id", sa.Integer(), nullable=True),
        sa.Column("crawl_page_id", sa.Integer(), nullable=True),
        sa.Column("family", sa.String(length=80), nullable=False),
        sa.Column("criterion", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_page_id"], ["crawl_pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seo_analysis_id"], ["seo_analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seo_page_analysis_id"], ["seo_page_analyses.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_seo_analysis_issues_code", "seo_analysis_issues", ["code"])
    op.create_index("ix_seo_analysis_issues_criterion", "seo_analysis_issues", ["criterion"])
    op.create_index("ix_seo_analysis_issues_crawl_page_id", "seo_analysis_issues", ["crawl_page_id"])
    op.create_index("ix_seo_analysis_issues_family", "seo_analysis_issues", ["family"])
    op.create_index("ix_seo_analysis_issues_id", "seo_analysis_issues", ["id"])
    op.create_index("ix_seo_analysis_issues_seo_analysis_id", "seo_analysis_issues", ["seo_analysis_id"])
    op.create_index(
        "ix_seo_analysis_issues_seo_page_analysis_id",
        "seo_analysis_issues",
        ["seo_page_analysis_id"],
    )
    op.create_index("ix_seo_analysis_issues_severity", "seo_analysis_issues", ["severity"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_seo_analysis_issues_severity", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_seo_page_analysis_id", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_seo_analysis_id", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_id", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_family", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_crawl_page_id", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_criterion", table_name="seo_analysis_issues")
    op.drop_index("ix_seo_analysis_issues_code", table_name="seo_analysis_issues")
    op.drop_table("seo_analysis_issues")

    op.drop_index("ix_seo_page_analyses_status", table_name="seo_page_analyses")
    op.drop_index("ix_seo_page_analyses_seo_analysis_id", table_name="seo_page_analyses")
    op.drop_index("ix_seo_page_analyses_id", table_name="seo_page_analyses")
    op.drop_index("ix_seo_page_analyses_crawl_page_id", table_name="seo_page_analyses")
    op.drop_table("seo_page_analyses")

    op.drop_index("ix_seo_analyses_status", table_name="seo_analyses")
    op.drop_index("ix_seo_analyses_id", table_name="seo_analyses")
    op.drop_index("ix_seo_analyses_crawl_session_id", table_name="seo_analyses")
    op.drop_table("seo_analyses")

