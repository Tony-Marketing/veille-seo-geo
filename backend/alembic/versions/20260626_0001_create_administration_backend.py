"""Create administration backend tables.

Revision ID: 20260626_0001
Revises:
Create Date: 2026-06-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260626_0001"
down_revision: str | None = None
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
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=150), nullable=False),
        sa.Column("label", sa.String(length=150), nullable=False),
        sa.Column("module", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *_timestamp_columns(),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)
    op.create_index("ix_permissions_module", "permissions", ["module"])

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamp_columns(),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superadmin", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamp_columns(),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "application_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("key", sa.String(length=150), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=30), nullable=False, server_default="string"),
        sa.Column("category", sa.String(length=80), nullable=False, server_default="global"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamp_columns(),
        sa.UniqueConstraint("key", name="uq_application_settings_key"),
    )
    op.create_index("ix_application_settings_category", "application_settings", ["category"])
    op.create_index("ix_application_settings_key", "application_settings", ["key"], unique=True)

    op.create_table(
        "ai_providers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("documentation_url", sa.String(length=255), nullable=True),
        sa.Column("default_model", sa.String(length=120), nullable=True),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("max_concurrent_requests", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
        sa.UniqueConstraint("name", name="uq_ai_providers_name"),
    )
    op.create_index("ix_ai_providers_name", "ai_providers", ["name"], unique=True)

    op.create_table(
        "ai_models",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("api_identifier", sa.String(length=150), nullable=False),
        sa.Column("input_cost", sa.Float(), nullable=True),
        sa.Column("output_cost", sa.Float(), nullable=True),
        sa.Column("max_context_tokens", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["provider_id"], ["ai_providers.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_ai_models_api_identifier", "ai_models", ["api_identifier"])
    op.create_index("ix_ai_models_provider_id", "ai_models", ["provider_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=True),
        sa.Column("provider_name", sa.String(length=120), nullable=True),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("value_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["provider_id"], ["ai_providers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("name", name="uq_api_keys_name"),
    )
    op.create_index("ix_api_keys_name", "api_keys", ["name"], unique=True)
    op.create_index("ix_api_keys_provider_name", "api_keys", ["provider_name"])
    op.create_index("ix_api_keys_value_fingerprint", "api_keys", ["value_fingerprint"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("level", sa.String(length=30), nullable=False, server_default="info"),
        sa.Column("ip_address", sa.String(length=80), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_level", "audit_logs", ["level"])
    op.create_index("ix_audit_logs_module", "audit_logs", ["module"])

    op.create_table(
        "error_logs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("exception", sa.String(length=255), nullable=False),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.Column("endpoint", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("environment", sa.String(length=50), nullable=False, server_default="development"),
        sa.Column("level", sa.String(length=30), nullable=False, server_default="error"),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("comment", sa.Text(), nullable=True),
        *_timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_error_logs_endpoint", "error_logs", ["endpoint"])
    op.create_index("ix_error_logs_level", "error_logs", ["level"])

    op.create_table(
        "system_parameters",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("key", sa.String(length=150), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=30), nullable=False, server_default="string"),
        sa.Column("description", sa.Text(), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_system_parameters_category", "system_parameters", ["category"])
    op.create_index("ix_system_parameters_key", "system_parameters", ["key"])


def downgrade() -> None:
    """Rollback migration."""

    op.drop_index("ix_system_parameters_key", table_name="system_parameters")
    op.drop_index("ix_system_parameters_category", table_name="system_parameters")
    op.drop_table("system_parameters")

    op.drop_index("ix_error_logs_level", table_name="error_logs")
    op.drop_index("ix_error_logs_endpoint", table_name="error_logs")
    op.drop_table("error_logs")

    op.drop_index("ix_audit_logs_module", table_name="audit_logs")
    op.drop_index("ix_audit_logs_level", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_api_keys_value_fingerprint", table_name="api_keys")
    op.drop_index("ix_api_keys_provider_name", table_name="api_keys")
    op.drop_index("ix_api_keys_name", table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_index("ix_ai_models_provider_id", table_name="ai_models")
    op.drop_index("ix_ai_models_api_identifier", table_name="ai_models")
    op.drop_table("ai_models")

    op.drop_index("ix_ai_providers_name", table_name="ai_providers")
    op.drop_table("ai_providers")

    op.drop_index("ix_application_settings_key", table_name="application_settings")
    op.drop_index("ix_application_settings_category", table_name="application_settings")
    op.drop_table("application_settings")

    op.drop_table("user_roles")
    op.drop_table("role_permissions")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")

    op.drop_index("ix_permissions_module", table_name="permissions")
    op.drop_index("ix_permissions_code", table_name="permissions")
    op.drop_table("permissions")
