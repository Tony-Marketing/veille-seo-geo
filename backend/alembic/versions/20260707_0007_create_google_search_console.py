"""Create Google Search Console tables.

Revision ID: 20260707_0007
Revises: 20260706_0006
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0007"
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
        "google_search_console_properties",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("google_property_id", sa.String(length=500), nullable=False),
        sa.Column("property_url", sa.String(length=500), nullable=False),
        sa.Column("property_type", sa.String(length=30), nullable=False, server_default="URL_PREFIX"),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("permission_level", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("encrypted_access_token", sa.Text(), nullable=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("token_scopes", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("google_property_id", name="uq_gsc_properties_google_property_id"),
    )
    op.create_index("ix_gsc_properties_google_property_id", "google_search_console_properties", ["google_property_id"])
    op.create_index("ix_gsc_properties_id", "google_search_console_properties", ["id"])
    op.create_index("ix_gsc_properties_is_active", "google_search_console_properties", ["is_active"])
    op.create_index("ix_gsc_properties_permission_level", "google_search_console_properties", ["permission_level"])
    op.create_index("ix_gsc_properties_property_type", "google_search_console_properties", ["property_type"])
    op.create_index("ix_gsc_properties_property_url", "google_search_console_properties", ["property_url"])
    op.create_index("ix_gsc_properties_website_id", "google_search_console_properties", ["website_id"])

    op.create_table(
        "google_search_console_imports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_type", sa.String(length=50), nullable=False, server_default="MANUAL"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("dimensions", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("rows_requested", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["google_search_console_properties.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_gsc_imports_end_date", "google_search_console_imports", ["end_date"])
    op.create_index("ix_gsc_imports_id", "google_search_console_imports", ["id"])
    op.create_index("ix_gsc_imports_import_type", "google_search_console_imports", ["import_type"])
    op.create_index("ix_gsc_imports_property_id", "google_search_console_imports", ["property_id"])
    op.create_index("ix_gsc_imports_start_date", "google_search_console_imports", ["start_date"])
    op.create_index("ix_gsc_imports_status", "google_search_console_imports", ["status"])

    op.create_table(
        "google_search_console_performances",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("query", sa.String(length=1000), nullable=True),
        sa.Column("page", sa.String(length=1000), nullable=True),
        sa.Column("country", sa.String(length=10), nullable=True),
        sa.Column("device", sa.String(length=40), nullable=True),
        sa.Column("search_type", sa.String(length=40), nullable=False, server_default="web"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ctr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("position", sa.Float(), nullable=False, server_default="0"),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_id"], ["google_search_console_imports.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["google_search_console_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "property_id",
            "date",
            "query",
            "page",
            "country",
            "device",
            "search_type",
            name="uq_gsc_performances_dimensions",
        ),
    )
    op.create_index("ix_gsc_performances_country", "google_search_console_performances", ["country"])
    op.create_index("ix_gsc_performances_date", "google_search_console_performances", ["date"])
    op.create_index("ix_gsc_performances_device", "google_search_console_performances", ["device"])
    op.create_index("ix_gsc_performances_id", "google_search_console_performances", ["id"])
    op.create_index("ix_gsc_performances_import_id", "google_search_console_performances", ["import_id"])
    op.create_index("ix_gsc_performances_page", "google_search_console_performances", ["page"])
    op.create_index("ix_gsc_performances_property_id", "google_search_console_performances", ["property_id"])
    op.create_index("ix_gsc_performances_query", "google_search_console_performances", ["query"])
    op.create_index("ix_gsc_performances_search_type", "google_search_console_performances", ["search_type"])

    op.create_table(
        "google_search_console_index_coverages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("coverage_state", sa.String(length=80), nullable=False),
        sa.Column("google_state", sa.String(length=120), nullable=True),
        sa.Column("indexing_state", sa.String(length=120), nullable=True),
        sa.Column("page_fetch_state", sa.String(length=120), nullable=True),
        sa.Column("robots_txt_state", sa.String(length=120), nullable=True),
        sa.Column("verdict", sa.String(length=80), nullable=True),
        sa.Column("issue_type", sa.String(length=255), nullable=True),
        sa.Column("sitemap", sa.String(length=1000), nullable=True),
        sa.Column("referring_urls", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("last_crawled_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_id"], ["google_search_console_imports.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["google_search_console_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "url", name="uq_gsc_index_coverages_property_url"),
    )
    op.create_index(
        "ix_gsc_index_coverages_coverage_state",
        "google_search_console_index_coverages",
        ["coverage_state"],
    )
    op.create_index("ix_gsc_index_coverages_google_state", "google_search_console_index_coverages", ["google_state"])
    op.create_index("ix_gsc_index_coverages_id", "google_search_console_index_coverages", ["id"])
    op.create_index("ix_gsc_index_coverages_import_id", "google_search_console_index_coverages", ["import_id"])
    op.create_index(
        "ix_gsc_index_coverages_indexing_state",
        "google_search_console_index_coverages",
        ["indexing_state"],
    )
    op.create_index("ix_gsc_index_coverages_issue_type", "google_search_console_index_coverages", ["issue_type"])
    op.create_index("ix_gsc_index_coverages_property_id", "google_search_console_index_coverages", ["property_id"])
    op.create_index("ix_gsc_index_coverages_url", "google_search_console_index_coverages", ["url"])
    op.create_index("ix_gsc_index_coverages_verdict", "google_search_console_index_coverages", ["verdict"])

    op.create_table(
        "google_search_console_sitemaps",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("sitemap_url", sa.String(length=1000), nullable=False),
        sa.Column("sitemap_type", sa.String(length=80), nullable=True),
        sa.Column("is_pending", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_sitemaps_index", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("warnings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("contents", sa.JSON(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_id"], ["google_search_console_imports.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["google_search_console_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "sitemap_url", name="uq_gsc_sitemaps_property_url"),
    )
    op.create_index("ix_gsc_sitemaps_id", "google_search_console_sitemaps", ["id"])
    op.create_index("ix_gsc_sitemaps_import_id", "google_search_console_sitemaps", ["import_id"])
    op.create_index("ix_gsc_sitemaps_property_id", "google_search_console_sitemaps", ["property_id"])
    op.create_index("ix_gsc_sitemaps_sitemap_type", "google_search_console_sitemaps", ["sitemap_type"])
    op.create_index("ix_gsc_sitemaps_sitemap_url", "google_search_console_sitemaps", ["sitemap_url"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_gsc_sitemaps_sitemap_url", table_name="google_search_console_sitemaps")
    op.drop_index("ix_gsc_sitemaps_sitemap_type", table_name="google_search_console_sitemaps")
    op.drop_index("ix_gsc_sitemaps_property_id", table_name="google_search_console_sitemaps")
    op.drop_index("ix_gsc_sitemaps_import_id", table_name="google_search_console_sitemaps")
    op.drop_index("ix_gsc_sitemaps_id", table_name="google_search_console_sitemaps")
    op.drop_table("google_search_console_sitemaps")

    op.drop_index("ix_gsc_index_coverages_verdict", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_url", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_property_id", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_issue_type", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_indexing_state", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_import_id", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_id", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_google_state", table_name="google_search_console_index_coverages")
    op.drop_index("ix_gsc_index_coverages_coverage_state", table_name="google_search_console_index_coverages")
    op.drop_table("google_search_console_index_coverages")

    op.drop_index("ix_gsc_performances_search_type", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_query", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_property_id", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_page", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_import_id", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_id", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_device", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_date", table_name="google_search_console_performances")
    op.drop_index("ix_gsc_performances_country", table_name="google_search_console_performances")
    op.drop_table("google_search_console_performances")

    op.drop_index("ix_gsc_imports_status", table_name="google_search_console_imports")
    op.drop_index("ix_gsc_imports_start_date", table_name="google_search_console_imports")
    op.drop_index("ix_gsc_imports_property_id", table_name="google_search_console_imports")
    op.drop_index("ix_gsc_imports_import_type", table_name="google_search_console_imports")
    op.drop_index("ix_gsc_imports_id", table_name="google_search_console_imports")
    op.drop_index("ix_gsc_imports_end_date", table_name="google_search_console_imports")
    op.drop_table("google_search_console_imports")

    op.drop_index("ix_gsc_properties_website_id", table_name="google_search_console_properties")
    op.drop_index("ix_gsc_properties_property_url", table_name="google_search_console_properties")
    op.drop_index("ix_gsc_properties_property_type", table_name="google_search_console_properties")
    op.drop_index("ix_gsc_properties_permission_level", table_name="google_search_console_properties")
    op.drop_index("ix_gsc_properties_is_active", table_name="google_search_console_properties")
    op.drop_index("ix_gsc_properties_id", table_name="google_search_console_properties")
    op.drop_index("ix_gsc_properties_google_property_id", table_name="google_search_console_properties")
    op.drop_table("google_search_console_properties")
