"""Create GEO analysis tables.

Revision ID: 20260706_0006
Revises: 20260703_0005
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260706_0006"
down_revision: str | None = "20260703_0005"
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
        "geo_analyses",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("seo_analysis_id", sa.Integer(), nullable=False),
        sa.Column("crawl_session_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("geo_score", sa.Float(), nullable=True),
        sa.Column("llm_score", sa.Float(), nullable=True),
        sa.Column("global_score", sa.Float(), nullable=True),
        sa.Column("providers_requested", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("pages_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pages_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provider_results_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recommendations_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_session_id"], ["crawl_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seo_analysis_id"], ["seo_analyses.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_geo_analyses_crawl_session_id", "geo_analyses", ["crawl_session_id"])
    op.create_index("ix_geo_analyses_id", "geo_analyses", ["id"])
    op.create_index("ix_geo_analyses_seo_analysis_id", "geo_analyses", ["seo_analysis_id"])
    op.create_index("ix_geo_analyses_status", "geo_analyses", ["status"])

    op.create_table(
        "geo_provider_results",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("geo_analysis_id", sa.Integer(), nullable=False),
        sa.Column("crawl_page_id", sa.Integer(), nullable=True),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("normalized_response", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_page_id"], ["crawl_pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["geo_analysis_id"], ["geo_analyses.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_geo_provider_results_crawl_page_id", "geo_provider_results", ["crawl_page_id"])
    op.create_index("ix_geo_provider_results_geo_analysis_id", "geo_provider_results", ["geo_analysis_id"])
    op.create_index("ix_geo_provider_results_id", "geo_provider_results", ["id"])
    op.create_index("ix_geo_provider_results_model_name", "geo_provider_results", ["model_name"])
    op.create_index("ix_geo_provider_results_provider_name", "geo_provider_results", ["provider_name"])
    op.create_index("ix_geo_provider_results_status", "geo_provider_results", ["status"])

    op.create_table(
        "geo_recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("geo_analysis_id", sa.Integer(), nullable=False),
        sa.Column("provider_result_id", sa.Integer(), nullable=True),
        sa.Column("crawl_page_id", sa.Integer(), nullable=True),
        sa.Column("recommendation_type", sa.String(length=30), nullable=False),
        sa.Column("severity", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=120), nullable=True),
        sa.Column("impact_score", sa.Float(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["crawl_page_id"], ["crawl_pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["geo_analysis_id"], ["geo_analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_result_id"], ["geo_provider_results.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_geo_recommendations_crawl_page_id", "geo_recommendations", ["crawl_page_id"])
    op.create_index("ix_geo_recommendations_geo_analysis_id", "geo_recommendations", ["geo_analysis_id"])
    op.create_index("ix_geo_recommendations_id", "geo_recommendations", ["id"])
    op.create_index("ix_geo_recommendations_priority", "geo_recommendations", ["priority"])
    op.create_index("ix_geo_recommendations_provider_result_id", "geo_recommendations", ["provider_result_id"])
    op.create_index("ix_geo_recommendations_recommendation_type", "geo_recommendations", ["recommendation_type"])
    op.create_index("ix_geo_recommendations_severity", "geo_recommendations", ["severity"])
    op.create_index("ix_geo_recommendations_source", "geo_recommendations", ["source"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_geo_recommendations_source", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_severity", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_recommendation_type", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_provider_result_id", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_priority", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_id", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_geo_analysis_id", table_name="geo_recommendations")
    op.drop_index("ix_geo_recommendations_crawl_page_id", table_name="geo_recommendations")
    op.drop_table("geo_recommendations")

    op.drop_index("ix_geo_provider_results_status", table_name="geo_provider_results")
    op.drop_index("ix_geo_provider_results_provider_name", table_name="geo_provider_results")
    op.drop_index("ix_geo_provider_results_model_name", table_name="geo_provider_results")
    op.drop_index("ix_geo_provider_results_id", table_name="geo_provider_results")
    op.drop_index("ix_geo_provider_results_geo_analysis_id", table_name="geo_provider_results")
    op.drop_index("ix_geo_provider_results_crawl_page_id", table_name="geo_provider_results")
    op.drop_table("geo_provider_results")

    op.drop_index("ix_geo_analyses_status", table_name="geo_analyses")
    op.drop_index("ix_geo_analyses_seo_analysis_id", table_name="geo_analyses")
    op.drop_index("ix_geo_analyses_id", table_name="geo_analyses")
    op.drop_index("ix_geo_analyses_crawl_session_id", table_name="geo_analyses")
    op.drop_table("geo_analyses")
