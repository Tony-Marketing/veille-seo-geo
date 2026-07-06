"""Add raw HTML to crawl pages.

Revision ID: 20260703_0005
Revises: 20260703_0004
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260703_0005"
down_revision: str | None = "20260703_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""

    op.add_column("crawl_pages", sa.Column("raw_html", sa.Text(), nullable=True))


def downgrade() -> None:
    """Rollback migration."""

    op.drop_column("crawl_pages", "raw_html")
