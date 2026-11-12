"""runtime endpoint (destino interno para o gateway)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-12
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("runtime_instances", sa.Column("endpoint_host", sa.String(length=255), nullable=True))
    op.add_column("runtime_instances", sa.Column("endpoint_port", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("runtime_instances", "endpoint_port")
    op.drop_column("runtime_instances", "endpoint_host")
