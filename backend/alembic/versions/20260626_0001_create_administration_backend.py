"""Create administration backend tables.

Revision ID: 20260626_0001
Revises:
Create Date: 2026-06-26
"""

from collections.abc import Sequence

from alembic import op

from backend.app import models  # noqa: F401
from backend.app.core.database import Base

revision: str = "20260626_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Rollback migration."""

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
