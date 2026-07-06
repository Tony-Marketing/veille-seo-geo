"""Create Google Search Console backend tables.

Revision ID: 20260706_0007
Revises: 20260706_0006
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260706_0007"
down_revision: str | None = "20260706_0006"
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
        "gsc_oauth_credentials",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False, server_default="google"),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("encrypted_access_token", sa.Text(), nullable=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_gsc_oauth_credentials_created_by_id", "gsc_oauth_credentials", ["created_by_id"])
    op.create_index("ix_gsc_oauth_credentials_id", "gsc_oauth_credentials", ["id"])
    op.create_index("ix_gsc_oauth_credentials_provider", "gsc_oauth_credentials", ["provider"])
    op.create_index("ix_gsc_oauth_credentials_status", "gsc_oauth_credentials", ["status"])
    op.create_index("ix_gsc_oauth_credentials_updated_by_id", "gsc_oauth_credentials", ["updated_by_id"])

    op.create_table(
        "gsc_properties",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("site_url", sa.String(length=500), nullable=False),
        sa.Column("property_type", sa.String(length=30), nullable=False, server_default="url_prefix"),
        sa.Column("permission_level", sa.String(length=80), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("site_url"),
    )
    op.create_index("ix_gsc_properties_id", "gsc_properties", ["id"])
    op.create_index("ix_gsc_properties_is_verified", "gsc_properties", ["is_verified"])
    op.create_index("ix_gsc_properties_property_type", "gsc_properties", ["property_type"])
    op.create_index("ix_gsc_properties_site_url", "gsc_properties", ["site_url"])
    op.create_index("ix_gsc_properties_website_id", "gsc_properties", ["website_id"])

    op.create_table(
        "gsc_import_runs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("import_type", sa.String(length=40), nullable=False, server_default="full"),
        sa.Column("date_start", sa.Date(), nullable=True),
        sa.Column("date_end", sa.Date(), nullable=True),
        sa.Column("rows_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_gsc_import_runs_id", "gsc_import_runs", ["id"])
    op.create_index("ix_gsc_import_runs_import_type", "gsc_import_runs", ["import_type"])
    op.create_index("ix_gsc_import_runs_property_id", "gsc_import_runs", ["property_id"])
    op.create_index("ix_gsc_import_runs_status", "gsc_import_runs", ["status"])

    op.create_table(
        "gsc_performance_daily",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_run_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("page", sa.String(length=1000), nullable=False, server_default=""),
        sa.Column("query", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("device", sa.String(length=40), nullable=False, server_default=""),
        sa.Column("country", sa.String(length=10), nullable=False, server_default=""),
        sa.Column("search_type", sa.String(length=40), nullable=False, server_default="web"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ctr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("position", sa.Float(), nullable=False, server_default="0"),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_run_id"], ["gsc_import_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "property_id",
            "date",
            "page",
            "query",
            "device",
            "country",
            "search_type",
            name="uq_gsc_performance_dimensions",
        ),
    )
    op.create_index("ix_gsc_performance_daily_country", "gsc_performance_daily", ["country"])
    op.create_index("ix_gsc_performance_daily_date", "gsc_performance_daily", ["date"])
    op.create_index("ix_gsc_performance_daily_device", "gsc_performance_daily", ["device"])
    op.create_index("ix_gsc_performance_daily_id", "gsc_performance_daily", ["id"])
    op.create_index("ix_gsc_performance_daily_import_run_id", "gsc_performance_daily", ["import_run_id"])
    op.create_index("ix_gsc_performance_daily_page", "gsc_performance_daily", ["page"])
    op.create_index("ix_gsc_performance_daily_property_id", "gsc_performance_daily", ["property_id"])
    op.create_index("ix_gsc_performance_daily_query", "gsc_performance_daily", ["query"])
    op.create_index("ix_gsc_performance_daily_search_type", "gsc_performance_daily", ["search_type"])

    op.create_table(
        "gsc_coverage_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_run_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=False),
        sa.Column("pages_count", sa.Integer(), nullable=False, server_default="0"),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_run_id"], ["gsc_import_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "date", "category", "state", name="uq_gsc_coverage_snapshot"),
    )
    op.create_index("ix_gsc_coverage_snapshots_category", "gsc_coverage_snapshots", ["category"])
    op.create_index("ix_gsc_coverage_snapshots_date", "gsc_coverage_snapshots", ["date"])
    op.create_index("ix_gsc_coverage_snapshots_id", "gsc_coverage_snapshots", ["id"])
    op.create_index("ix_gsc_coverage_snapshots_import_run_id", "gsc_coverage_snapshots", ["import_run_id"])
    op.create_index("ix_gsc_coverage_snapshots_property_id", "gsc_coverage_snapshots", ["property_id"])
    op.create_index("ix_gsc_coverage_snapshots_state", "gsc_coverage_snapshots", ["state"])

    op.create_table(
        "gsc_indexing_inspections",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_run_id", sa.Integer(), nullable=True),
        sa.Column("inspected_url", sa.String(length=1000), nullable=False),
        sa.Column("coverage_state", sa.String(length=120), nullable=True),
        sa.Column("indexing_state", sa.String(length=120), nullable=True),
        sa.Column("verdict", sa.String(length=80), nullable=True),
        sa.Column("robots_txt_state", sa.String(length=120), nullable=True),
        sa.Column("page_fetch_state", sa.String(length=120), nullable=True),
        sa.Column("google_canonical", sa.String(length=1000), nullable=True),
        sa.Column("user_canonical", sa.String(length=1000), nullable=True),
        sa.Column("last_crawl_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_run_id"], ["gsc_import_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "inspected_url", "inspected_at", name="uq_gsc_indexing_inspection"),
    )
    op.create_index("ix_gsc_indexing_inspections_coverage_state", "gsc_indexing_inspections", ["coverage_state"])
    op.create_index("ix_gsc_indexing_inspections_id", "gsc_indexing_inspections", ["id"])
    op.create_index("ix_gsc_indexing_inspections_import_run_id", "gsc_indexing_inspections", ["import_run_id"])
    op.create_index("ix_gsc_indexing_inspections_indexing_state", "gsc_indexing_inspections", ["indexing_state"])
    op.create_index("ix_gsc_indexing_inspections_inspected_at", "gsc_indexing_inspections", ["inspected_at"])
    op.create_index("ix_gsc_indexing_inspections_inspected_url", "gsc_indexing_inspections", ["inspected_url"])
    op.create_index("ix_gsc_indexing_inspections_property_id", "gsc_indexing_inspections", ["property_id"])
    op.create_index("ix_gsc_indexing_inspections_verdict", "gsc_indexing_inspections", ["verdict"])

    op.create_table(
        "gsc_sitemaps",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_run_id", sa.Integer(), nullable=True),
        sa.Column("sitemap_url", sa.String(length=1000), nullable=False),
        sa.Column("path", sa.String(length=1000), nullable=True),
        sa.Column("last_submitted", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_downloaded", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_pending", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_sitemaps_index", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sitemap_type", sa.String(length=80), nullable=True),
        sa.Column("errors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warnings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("contents", sa.JSON(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_run_id"], ["gsc_import_runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "sitemap_url", name="uq_gsc_sitemaps_property_url"),
    )
    op.create_index("ix_gsc_sitemaps_id", "gsc_sitemaps", ["id"])
    op.create_index("ix_gsc_sitemaps_import_run_id", "gsc_sitemaps", ["import_run_id"])
    op.create_index("ix_gsc_sitemaps_property_id", "gsc_sitemaps", ["property_id"])
    op.create_index("ix_gsc_sitemaps_sitemap_url", "gsc_sitemaps", ["sitemap_url"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_gsc_sitemaps_sitemap_url", table_name="gsc_sitemaps")
    op.drop_index("ix_gsc_sitemaps_property_id", table_name="gsc_sitemaps")
    op.drop_index("ix_gsc_sitemaps_import_run_id", table_name="gsc_sitemaps")
    op.drop_index("ix_gsc_sitemaps_id", table_name="gsc_sitemaps")
    op.drop_table("gsc_sitemaps")

    op.drop_index("ix_gsc_indexing_inspections_verdict", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_property_id", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_inspected_url", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_inspected_at", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_indexing_state", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_import_run_id", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_id", table_name="gsc_indexing_inspections")
    op.drop_index("ix_gsc_indexing_inspections_coverage_state", table_name="gsc_indexing_inspections")
    op.drop_table("gsc_indexing_inspections")

    op.drop_index("ix_gsc_coverage_snapshots_state", table_name="gsc_coverage_snapshots")
    op.drop_index("ix_gsc_coverage_snapshots_property_id", table_name="gsc_coverage_snapshots")
    op.drop_index("ix_gsc_coverage_snapshots_import_run_id", table_name="gsc_coverage_snapshots")
    op.drop_index("ix_gsc_coverage_snapshots_id", table_name="gsc_coverage_snapshots")
    op.drop_index("ix_gsc_coverage_snapshots_date", table_name="gsc_coverage_snapshots")
    op.drop_index("ix_gsc_coverage_snapshots_category", table_name="gsc_coverage_snapshots")
    op.drop_table("gsc_coverage_snapshots")

    op.drop_index("ix_gsc_performance_daily_search_type", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_query", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_property_id", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_page", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_import_run_id", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_id", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_device", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_date", table_name="gsc_performance_daily")
    op.drop_index("ix_gsc_performance_daily_country", table_name="gsc_performance_daily")
    op.drop_table("gsc_performance_daily")

    op.drop_index("ix_gsc_import_runs_status", table_name="gsc_import_runs")
    op.drop_index("ix_gsc_import_runs_property_id", table_name="gsc_import_runs")
    op.drop_index("ix_gsc_import_runs_import_type", table_name="gsc_import_runs")
    op.drop_index("ix_gsc_import_runs_id", table_name="gsc_import_runs")
    op.drop_table("gsc_import_runs")

    op.drop_index("ix_gsc_properties_website_id", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_site_url", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_property_type", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_is_verified", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_id", table_name="gsc_properties")
    op.drop_table("gsc_properties")

    op.drop_index("ix_gsc_oauth_credentials_updated_by_id", table_name="gsc_oauth_credentials")
    op.drop_index("ix_gsc_oauth_credentials_status", table_name="gsc_oauth_credentials")
    op.drop_index("ix_gsc_oauth_credentials_provider", table_name="gsc_oauth_credentials")
    op.drop_index("ix_gsc_oauth_credentials_id", table_name="gsc_oauth_credentials")
    op.drop_index("ix_gsc_oauth_credentials_created_by_id", table_name="gsc_oauth_credentials")
    op.drop_table("gsc_oauth_credentials")
