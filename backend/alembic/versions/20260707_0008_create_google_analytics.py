"""Create Google Analytics tables.

Revision ID: 20260707_0008
Revises: 20260707_0007
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260707_0008"
down_revision: str | None = "20260707_0007"
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
        "google_analytics_properties",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("property_id", sa.String(length=100), nullable=False),
        sa.Column("property_name", sa.String(length=255), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=True),
        sa.Column("measurement_id", sa.String(length=80), nullable=True),
        sa.Column("encrypted_access_token", sa.Text(), nullable=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("property_id", name="uq_ga_properties_property_id"),
    )
    op.create_index("ix_ga_properties_account_name", "google_analytics_properties", ["account_name"])
    op.create_index("ix_ga_properties_enabled", "google_analytics_properties", ["enabled"])
    op.create_index("ix_ga_properties_id", "google_analytics_properties", ["id"])
    op.create_index("ix_ga_properties_measurement_id", "google_analytics_properties", ["measurement_id"])
    op.create_index("ix_ga_properties_property_id", "google_analytics_properties", ["property_id"])
    op.create_index("ix_ga_properties_property_name", "google_analytics_properties", ["property_name"])
    op.create_index("ix_ga_properties_website_id", "google_analytics_properties", ["website_id"])

    op.create_table(
        "google_analytics_imports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("imported_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["property_id"], ["google_analytics_properties.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_ga_imports_id", "google_analytics_imports", ["id"])
    op.create_index("ix_ga_imports_property_id", "google_analytics_imports", ["property_id"])
    op.create_index("ix_ga_imports_status", "google_analytics_imports", ["status"])

    op.create_table(
        "google_analytics_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("medium", sa.String(length=255), nullable=True),
        sa.Column("campaign", sa.String(length=255), nullable=True),
        sa.Column("device_category", sa.String(length=80), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_users", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sessions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engaged_sessions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("screen_page_views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_session_duration", sa.Float(), nullable=False, server_default="0"),
        sa.Column("engagement_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("conversions", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_revenue", sa.Float(), nullable=False, server_default="0"),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["import_id"], ["google_analytics_imports.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["property_id"], ["google_analytics_properties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "property_id",
            "date",
            "source",
            "medium",
            "campaign",
            "device_category",
            "country",
            name="uq_ga_metrics_property_date_dimensions",
        ),
    )
    op.create_index("ix_ga_metrics_campaign", "google_analytics_metrics", ["campaign"])
    op.create_index("ix_ga_metrics_country", "google_analytics_metrics", ["country"])
    op.create_index("ix_ga_metrics_date", "google_analytics_metrics", ["date"])
    op.create_index("ix_ga_metrics_device_category", "google_analytics_metrics", ["device_category"])
    op.create_index("ix_ga_metrics_id", "google_analytics_metrics", ["id"])
    op.create_index("ix_ga_metrics_import_id", "google_analytics_metrics", ["import_id"])
    op.create_index("ix_ga_metrics_medium", "google_analytics_metrics", ["medium"])
    op.create_index("ix_ga_metrics_property_id", "google_analytics_metrics", ["property_id"])
    op.create_index("ix_ga_metrics_source", "google_analytics_metrics", ["source"])

    op.create_table(
        "google_analytics_dimensions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("metric_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("medium", sa.String(length=255), nullable=True),
        sa.Column("campaign", sa.String(length=255), nullable=True),
        sa.Column("device_category", sa.String(length=80), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["metric_id"], ["google_analytics_metrics.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("metric_id", name="uq_ga_dimensions_metric_id"),
    )
    op.create_index("ix_ga_dimensions_campaign", "google_analytics_dimensions", ["campaign"])
    op.create_index("ix_ga_dimensions_country", "google_analytics_dimensions", ["country"])
    op.create_index("ix_ga_dimensions_device_category", "google_analytics_dimensions", ["device_category"])
    op.create_index("ix_ga_dimensions_id", "google_analytics_dimensions", ["id"])
    op.create_index("ix_ga_dimensions_medium", "google_analytics_dimensions", ["medium"])
    op.create_index("ix_ga_dimensions_metric_id", "google_analytics_dimensions", ["metric_id"])
    op.create_index("ix_ga_dimensions_source", "google_analytics_dimensions", ["source"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_ga_dimensions_source", table_name="google_analytics_dimensions")
    op.drop_index("ix_ga_dimensions_metric_id", table_name="google_analytics_dimensions")
    op.drop_index("ix_ga_dimensions_medium", table_name="google_analytics_dimensions")
    op.drop_index("ix_ga_dimensions_id", table_name="google_analytics_dimensions")
    op.drop_index("ix_ga_dimensions_device_category", table_name="google_analytics_dimensions")
    op.drop_index("ix_ga_dimensions_country", table_name="google_analytics_dimensions")
    op.drop_index("ix_ga_dimensions_campaign", table_name="google_analytics_dimensions")
    op.drop_table("google_analytics_dimensions")

    op.drop_index("ix_ga_metrics_source", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_property_id", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_medium", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_import_id", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_id", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_device_category", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_date", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_country", table_name="google_analytics_metrics")
    op.drop_index("ix_ga_metrics_campaign", table_name="google_analytics_metrics")
    op.drop_table("google_analytics_metrics")

    op.drop_index("ix_ga_imports_status", table_name="google_analytics_imports")
    op.drop_index("ix_ga_imports_property_id", table_name="google_analytics_imports")
    op.drop_index("ix_ga_imports_id", table_name="google_analytics_imports")
    op.drop_table("google_analytics_imports")

    op.drop_index("ix_ga_properties_website_id", table_name="google_analytics_properties")
    op.drop_index("ix_ga_properties_property_name", table_name="google_analytics_properties")
    op.drop_index("ix_ga_properties_property_id", table_name="google_analytics_properties")
    op.drop_index("ix_ga_properties_measurement_id", table_name="google_analytics_properties")
    op.drop_index("ix_ga_properties_id", table_name="google_analytics_properties")
    op.drop_index("ix_ga_properties_enabled", table_name="google_analytics_properties")
    op.drop_index("ix_ga_properties_account_name", table_name="google_analytics_properties")
    op.drop_table("google_analytics_properties")
