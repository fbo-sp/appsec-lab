"""session usage, idle tracking and attempt activity (ADR-014)

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-13 19:30:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("lab_sessions", sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("lab_sessions", sa.Column("end_reason", sa.String(24), nullable=True))
    op.add_column("lab_sessions", sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True))
    op.create_table(
        "attempt_activity",
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("minute", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["lab_attempts.id"], name=op.f("fk_attempt_activity_attempt_id_lab_attempts")
        ),
        sa.PrimaryKeyConstraint("attempt_id", "minute", name=op.f("pk_attempt_activity")),
    )
    op.execute("UPDATE lab_sessions SET last_activity_at = ready_at WHERE ready_at IS NOT NULL")
    # Sessões já encerradas: melhor aproximação disponível (última atualização, limitada ao prazo).
    op.execute(
        "UPDATE lab_sessions SET ended_at = LEAST(updated_at, expires_at) "
        "WHERE status NOT IN ('REQUESTED','PROVISIONING','READY','ACTIVE')"
    )


def downgrade() -> None:
    op.drop_table("attempt_activity")
    op.drop_column("lab_sessions", "last_activity_at")
    op.drop_column("lab_sessions", "end_reason")
    op.drop_column("lab_sessions", "ended_at")
