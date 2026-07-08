"""Create Bing Webmaster Tools tables.

Revision ID: 20260708_0009
Revises: 20260707_0008
Create Date: 2026-07-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260708_0009"
down_revision: str | None = "20260707_0008"
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
        "bing_webmaster_connections",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("auth_type", sa.String(length=30), nullable=False, server_default="API_KEY"),
        sa.Column("client_id", sa.String(length=255), nullable=True),
        sa.Column("client_secret_encrypted", sa.Text(), nullable=True),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_bing_connections_auth_type", "bing_webmaster_connections", ["auth_type"])
    op.create_index("ix_bing_connections_client_id", "bing_webmaster_connections", ["client_id"])
    op.create_index("ix_bing_connections_id", "bing_webmaster_connections", ["id"])
    op.create_index("ix_bing_connections_is_active", "bing_webmaster_connections", ["is_active"])
    op.create_index("ix_bing_connections_website_id", "bing_webmaster_connections", ["website_id"])

    op.create_table(
        "bing_webmaster_sites",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("site_url", sa.String(length=1000), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_import_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["connection_id"], ["bing_webmaster_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
    )
    op.create_unique_constraint("uq_bing_sites_connection_url", "bing_webmaster_sites", ["connection_id", "site_url"])
    op.create_index("ix_bing_sites_connection_id", "bing_webmaster_sites", ["connection_id"])
    op.create_index("ix_bing_sites_id", "bing_webmaster_sites", ["id"])
    op.create_index("ix_bing_sites_is_active", "bing_webmaster_sites", ["is_active"])
    op.create_index("ix_bing_sites_is_verified", "bing_webmaster_sites", ["is_verified"])
    op.create_index("ix_bing_sites_site_url", "bing_webmaster_sites", ["site_url"])
    op.create_index("ix_bing_sites_website_id", "bing_webmaster_sites", ["website_id"])

    op.create_table(
        "bing_webmaster_import_runs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("bing_site_id", sa.Integer(), nullable=True),
        sa.Column("import_type", sa.String(length=50), nullable=False, server_default="MANUAL"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bing_site_id"], ["bing_webmaster_sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["connection_id"], ["bing_webmaster_connections.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_bing_import_runs_bing_site_id", "bing_webmaster_import_runs", ["bing_site_id"])
    op.create_index("ix_bing_import_runs_connection_id", "bing_webmaster_import_runs", ["connection_id"])
    op.create_index("ix_bing_import_runs_id", "bing_webmaster_import_runs", ["id"])
    op.create_index("ix_bing_import_runs_import_type", "bing_webmaster_import_runs", ["import_type"])
    op.create_index("ix_bing_import_runs_status", "bing_webmaster_import_runs", ["status"])

    op.create_table(
        "bing_webmaster_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("bing_site_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("query", sa.String(length=1000), nullable=True),
        sa.Column("page_url", sa.String(length=1000), nullable=True),
        sa.Column("country", sa.String(length=10), nullable=True),
        sa.Column("device", sa.String(length=40), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ctr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("average_position", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bing_site_id"], ["bing_webmaster_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_id"], ["bing_webmaster_import_runs.id"], ondelete="SET NULL"),
    )
    op.create_unique_constraint(
        "uq_bing_metrics_site_dimensions",
        "bing_webmaster_metrics",
        ["bing_site_id", "date", "query", "page_url", "country", "device"],
    )
    op.create_index("ix_bing_metrics_bing_site_id", "bing_webmaster_metrics", ["bing_site_id"])
    op.create_index("ix_bing_metrics_country", "bing_webmaster_metrics", ["country"])
    op.create_index("ix_bing_metrics_date", "bing_webmaster_metrics", ["date"])
    op.create_index("ix_bing_metrics_device", "bing_webmaster_metrics", ["device"])
    op.create_index("ix_bing_metrics_id", "bing_webmaster_metrics", ["id"])
    op.create_index("ix_bing_metrics_import_id", "bing_webmaster_metrics", ["import_id"])
    op.create_index("ix_bing_metrics_page_url", "bing_webmaster_metrics", ["page_url"])
    op.create_index("ix_bing_metrics_query", "bing_webmaster_metrics", ["query"])

    op.create_table(
        "bing_webmaster_crawl_stats",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("bing_site_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("issue_type", sa.String(length=255), nullable=True),
        sa.Column("issue_category", sa.String(length=255), nullable=True),
        sa.Column("severity", sa.String(length=80), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bing_site_id"], ["bing_webmaster_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_id"], ["bing_webmaster_import_runs.id"], ondelete="SET NULL"),
    )
    op.create_unique_constraint(
        "uq_bing_crawl_stats_site_issue",
        "bing_webmaster_crawl_stats",
        ["bing_site_id", "date", "url", "http_status", "issue_type"],
    )
    op.create_index("ix_bing_crawl_stats_bing_site_id", "bing_webmaster_crawl_stats", ["bing_site_id"])
    op.create_index("ix_bing_crawl_stats_date", "bing_webmaster_crawl_stats", ["date"])
    op.create_index("ix_bing_crawl_stats_http_status", "bing_webmaster_crawl_stats", ["http_status"])
    op.create_index("ix_bing_crawl_stats_id", "bing_webmaster_crawl_stats", ["id"])
    op.create_index("ix_bing_crawl_stats_import_id", "bing_webmaster_crawl_stats", ["import_id"])
    op.create_index("ix_bing_crawl_stats_issue_category", "bing_webmaster_crawl_stats", ["issue_category"])
    op.create_index("ix_bing_crawl_stats_issue_type", "bing_webmaster_crawl_stats", ["issue_type"])
    op.create_index("ix_bing_crawl_stats_severity", "bing_webmaster_crawl_stats", ["severity"])
    op.create_index("ix_bing_crawl_stats_url", "bing_webmaster_crawl_stats", ["url"])

    op.create_table(
        "bing_webmaster_sitemaps",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("bing_site_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("sitemap_url", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_crawled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("url_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["bing_site_id"], ["bing_webmaster_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["import_id"], ["bing_webmaster_import_runs.id"], ondelete="SET NULL"),
    )
    op.create_unique_constraint("uq_bing_sitemaps_site_url", "bing_webmaster_sitemaps", ["bing_site_id", "sitemap_url"])
    op.create_index("ix_bing_sitemaps_bing_site_id", "bing_webmaster_sitemaps", ["bing_site_id"])
    op.create_index("ix_bing_sitemaps_id", "bing_webmaster_sitemaps", ["id"])
    op.create_index("ix_bing_sitemaps_import_id", "bing_webmaster_sitemaps", ["import_id"])
    op.create_index("ix_bing_sitemaps_sitemap_url", "bing_webmaster_sitemaps", ["sitemap_url"])
    op.create_index("ix_bing_sitemaps_status", "bing_webmaster_sitemaps", ["status"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_bing_sitemaps_status", table_name="bing_webmaster_sitemaps")
    op.drop_index("ix_bing_sitemaps_sitemap_url", table_name="bing_webmaster_sitemaps")
    op.drop_index("ix_bing_sitemaps_import_id", table_name="bing_webmaster_sitemaps")
    op.drop_index("ix_bing_sitemaps_id", table_name="bing_webmaster_sitemaps")
    op.drop_index("ix_bing_sitemaps_bing_site_id", table_name="bing_webmaster_sitemaps")
    op.drop_table("bing_webmaster_sitemaps")

    op.drop_index("ix_bing_crawl_stats_url", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_severity", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_issue_type", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_issue_category", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_import_id", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_id", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_http_status", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_date", table_name="bing_webmaster_crawl_stats")
    op.drop_index("ix_bing_crawl_stats_bing_site_id", table_name="bing_webmaster_crawl_stats")
    op.drop_table("bing_webmaster_crawl_stats")

    op.drop_index("ix_bing_metrics_query", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_page_url", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_import_id", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_id", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_device", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_date", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_country", table_name="bing_webmaster_metrics")
    op.drop_index("ix_bing_metrics_bing_site_id", table_name="bing_webmaster_metrics")
    op.drop_table("bing_webmaster_metrics")

    op.drop_index("ix_bing_import_runs_status", table_name="bing_webmaster_import_runs")
    op.drop_index("ix_bing_import_runs_import_type", table_name="bing_webmaster_import_runs")
    op.drop_index("ix_bing_import_runs_id", table_name="bing_webmaster_import_runs")
    op.drop_index("ix_bing_import_runs_connection_id", table_name="bing_webmaster_import_runs")
    op.drop_index("ix_bing_import_runs_bing_site_id", table_name="bing_webmaster_import_runs")
    op.drop_table("bing_webmaster_import_runs")

    op.drop_index("ix_bing_sites_website_id", table_name="bing_webmaster_sites")
    op.drop_index("ix_bing_sites_site_url", table_name="bing_webmaster_sites")
    op.drop_index("ix_bing_sites_is_verified", table_name="bing_webmaster_sites")
    op.drop_index("ix_bing_sites_is_active", table_name="bing_webmaster_sites")
    op.drop_index("ix_bing_sites_id", table_name="bing_webmaster_sites")
    op.drop_index("ix_bing_sites_connection_id", table_name="bing_webmaster_sites")
    op.drop_table("bing_webmaster_sites")

    op.drop_index("ix_bing_connections_website_id", table_name="bing_webmaster_connections")
    op.drop_index("ix_bing_connections_is_active", table_name="bing_webmaster_connections")
    op.drop_index("ix_bing_connections_id", table_name="bing_webmaster_connections")
    op.drop_index("ix_bing_connections_client_id", table_name="bing_webmaster_connections")
    op.drop_index("ix_bing_connections_auth_type", table_name="bing_webmaster_connections")
    op.drop_table("bing_webmaster_connections")
