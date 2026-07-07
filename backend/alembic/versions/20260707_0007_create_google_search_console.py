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
        "gsc_properties",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("site_url", sa.String(length=500), nullable=False),
        sa.Column("property_type", sa.String(length=40), nullable=False, server_default="URL_PREFIX"),
        sa.Column("permission_level", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("site_url", name="uq_gsc_properties_site_url"),
    )
    op.create_index("ix_gsc_properties_id", "gsc_properties", ["id"])
    op.create_index("ix_gsc_properties_property_type", "gsc_properties", ["property_type"])
    op.create_index("ix_gsc_properties_site_url", "gsc_properties", ["site_url"], unique=True)
    op.create_index("ix_gsc_properties_status", "gsc_properties", ["status"])
    op.create_index("ix_gsc_properties_website_id", "gsc_properties", ["website_id"])

    op.create_table(
        "gsc_performances",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("page", sa.String(length=1000), nullable=True),
        sa.Column("query", sa.String(length=500), nullable=True),
        sa.Column("country", sa.String(length=10), nullable=True),
        sa.Column("device", sa.String(length=30), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ctr", sa.Float(), nullable=False, server_default="0"),
        sa.Column("position", sa.Float(), nullable=False, server_default="0"),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "property_id",
            "date",
            "page",
            "query",
            "country",
            "device",
            name="uq_gsc_performances_dimensions",
        ),
    )
    op.create_index("ix_gsc_performances_country", "gsc_performances", ["country"])
    op.create_index("ix_gsc_performances_date", "gsc_performances", ["date"])
    op.create_index("ix_gsc_performances_device", "gsc_performances", ["device"])
    op.create_index("ix_gsc_performances_id", "gsc_performances", ["id"])
    op.create_index("ix_gsc_performances_page", "gsc_performances", ["page"])
    op.create_index("ix_gsc_performances_property_id", "gsc_performances", ["property_id"])
    op.create_index("ix_gsc_performances_query", "gsc_performances", ["query"])

    op.create_table(
        "gsc_index_coverages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("coverage_state", sa.String(length=120), nullable=False),
        sa.Column("indexing_state", sa.String(length=120), nullable=True),
        sa.Column("verdict", sa.String(length=80), nullable=True),
        sa.Column("page_fetch_state", sa.String(length=120), nullable=True),
        sa.Column("google_canonical", sa.String(length=1000), nullable=True),
        sa.Column("user_canonical", sa.String(length=1000), nullable=True),
        sa.Column("last_crawl_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("inspected_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "url", name="uq_gsc_index_coverages_property_url"),
    )
    op.create_index("ix_gsc_index_coverages_coverage_state", "gsc_index_coverages", ["coverage_state"])
    op.create_index("ix_gsc_index_coverages_id", "gsc_index_coverages", ["id"])
    op.create_index("ix_gsc_index_coverages_indexing_state", "gsc_index_coverages", ["indexing_state"])
    op.create_index("ix_gsc_index_coverages_property_id", "gsc_index_coverages", ["property_id"])
    op.create_index("ix_gsc_index_coverages_url", "gsc_index_coverages", ["url"])
    op.create_index("ix_gsc_index_coverages_verdict", "gsc_index_coverages", ["verdict"])

    op.create_table(
        "gsc_sitemaps",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("sitemap_url", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("last_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("warnings", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("contents", sa.JSON(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("property_id", "sitemap_url", name="uq_gsc_sitemaps_property_url"),
    )
    op.create_index("ix_gsc_sitemaps_id", "gsc_sitemaps", ["id"])
    op.create_index("ix_gsc_sitemaps_property_id", "gsc_sitemaps", ["property_id"])
    op.create_index("ix_gsc_sitemaps_sitemap_url", "gsc_sitemaps", ["sitemap_url"])
    op.create_index("ix_gsc_sitemaps_status", "gsc_sitemaps", ["status"])

    op.create_table(
        "gsc_imports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=True),
        sa.Column("import_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("import_metadata", sa.JSON(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["gsc_properties.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_gsc_imports_finished_at", "gsc_imports", ["finished_at"])
    op.create_index("ix_gsc_imports_id", "gsc_imports", ["id"])
    op.create_index("ix_gsc_imports_import_type", "gsc_imports", ["import_type"])
    op.create_index("ix_gsc_imports_property_id", "gsc_imports", ["property_id"])
    op.create_index("ix_gsc_imports_started_at", "gsc_imports", ["started_at"])
    op.create_index("ix_gsc_imports_status", "gsc_imports", ["status"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_gsc_imports_status", table_name="gsc_imports")
    op.drop_index("ix_gsc_imports_started_at", table_name="gsc_imports")
    op.drop_index("ix_gsc_imports_property_id", table_name="gsc_imports")
    op.drop_index("ix_gsc_imports_import_type", table_name="gsc_imports")
    op.drop_index("ix_gsc_imports_id", table_name="gsc_imports")
    op.drop_index("ix_gsc_imports_finished_at", table_name="gsc_imports")
    op.drop_table("gsc_imports")

    op.drop_index("ix_gsc_sitemaps_status", table_name="gsc_sitemaps")
    op.drop_index("ix_gsc_sitemaps_sitemap_url", table_name="gsc_sitemaps")
    op.drop_index("ix_gsc_sitemaps_property_id", table_name="gsc_sitemaps")
    op.drop_index("ix_gsc_sitemaps_id", table_name="gsc_sitemaps")
    op.drop_table("gsc_sitemaps")

    op.drop_index("ix_gsc_index_coverages_verdict", table_name="gsc_index_coverages")
    op.drop_index("ix_gsc_index_coverages_url", table_name="gsc_index_coverages")
    op.drop_index("ix_gsc_index_coverages_property_id", table_name="gsc_index_coverages")
    op.drop_index("ix_gsc_index_coverages_indexing_state", table_name="gsc_index_coverages")
    op.drop_index("ix_gsc_index_coverages_id", table_name="gsc_index_coverages")
    op.drop_index("ix_gsc_index_coverages_coverage_state", table_name="gsc_index_coverages")
    op.drop_table("gsc_index_coverages")

    op.drop_index("ix_gsc_performances_query", table_name="gsc_performances")
    op.drop_index("ix_gsc_performances_property_id", table_name="gsc_performances")
    op.drop_index("ix_gsc_performances_page", table_name="gsc_performances")
    op.drop_index("ix_gsc_performances_id", table_name="gsc_performances")
    op.drop_index("ix_gsc_performances_device", table_name="gsc_performances")
    op.drop_index("ix_gsc_performances_date", table_name="gsc_performances")
    op.drop_index("ix_gsc_performances_country", table_name="gsc_performances")
    op.drop_table("gsc_performances")

    op.drop_index("ix_gsc_properties_website_id", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_status", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_site_url", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_property_type", table_name="gsc_properties")
    op.drop_index("ix_gsc_properties_id", table_name="gsc_properties")
    op.drop_table("gsc_properties")
