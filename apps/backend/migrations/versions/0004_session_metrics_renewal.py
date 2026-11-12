"""session metrics and renewal

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-12 20:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("lab_sessions", sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("lab_sessions", sa.Column("provision_ms", sa.Integer(), nullable=True))
    op.add_column("lab_sessions", sa.Column("renewals", sa.Integer(), server_default="0", nullable=False))
    op.add_column("lab_variants", sa.Column("max_renewals", sa.Integer(), server_default="2", nullable=False))
    op.create_index("ix_lab_sessions_ready_at", "lab_sessions", ["ready_at"])


def downgrade() -> None:
    op.drop_index("ix_lab_sessions_ready_at", table_name="lab_sessions")
    op.drop_column("lab_variants", "max_renewals")
    op.drop_column("lab_sessions", "renewals")
    op.drop_column("lab_sessions", "provision_ms")
    op.drop_column("lab_sessions", "ready_at")
