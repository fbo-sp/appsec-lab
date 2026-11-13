"""Modelos persistentes da 1ª fatia (docs/12_DATA_MODEL.md, ajustes G-10 de docs/22)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")
TZ = DateTime(timezone=True)

ACTIVE_SESSION_STATUSES = ("REQUESTED", "PROVISIONING", "READY", "ACTIVE")
_active_sql = ", ".join(f"'{s}'" for s in ACTIVE_SESSION_STATUSES)


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idp_subject: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(TZ)


class Lab(Base):
    __tablename__ = "labs"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    primary_cwe: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(TZ)


class LabRelease(Base):
    """Versão publicada e imutável (= "LaboratoryVersion" do PRD, ver G-01)."""

    __tablename__ = "lab_releases"
    __table_args__ = (
        UniqueConstraint("lab_id", "version", name="uq_lab_releases_lab_version"),
        CheckConstraint("status IN ('draft','published','retired')", name="status"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_id: Mapped[str] = mapped_column(ForeignKey("labs.id"))
    version: Mapped[str] = mapped_column(String(32))
    manifest_digest: Mapped[str] = mapped_column(String(80))
    manifest: Mapped[dict[str, Any]] = mapped_column(JsonType)
    status: Mapped[str] = mapped_column(String(16))
    published_at: Mapped[datetime | None] = mapped_column(TZ)
    created_at: Mapped[datetime] = mapped_column(TZ)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))


class LabVariant(Base):
    __tablename__ = "lab_variants"
    __table_args__ = (UniqueConstraint("release_id", "variant_key", name="uq_lab_variants_release_key"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_releases.id"))
    variant_key: Mapped[str] = mapped_column(String(63))
    language: Mapped[str] = mapped_column(String(63))
    framework: Mapped[str] = mapped_column(String(63))
    image_digest: Mapped[str] = mapped_column(String(255))
    runtime_profile: Mapped[str] = mapped_column(String(63))
    ttl_minutes: Mapped[int] = mapped_column(Integer)
    max_renewals: Mapped[int] = mapped_column(Integer, default=2, server_default="2")


class LabStep(Base):
    __tablename__ = "lab_steps"
    __table_args__ = (
        UniqueConstraint("release_id", "step_key", name="uq_lab_steps_release_key"),
        UniqueConstraint("release_id", "position", name="uq_lab_steps_release_position"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    release_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_releases.id"))
    step_key: Mapped[str] = mapped_column(String(63))
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    # validator_ref é dado protegido: nunca exposto em respostas a alunos.
    validator_ref: Mapped[str] = mapped_column(String(200))
    max_points: Mapped[int] = mapped_column(Integer)


class StepHint(Base):
    __tablename__ = "step_hints"
    __table_args__ = (UniqueConstraint("step_id", "level", name="uq_step_hints_step_level"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_steps.id"))
    level: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)


class LabSession(Base):
    __tablename__ = "lab_sessions"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_lab_sessions_user_idem"),
        CheckConstraint(
            "status IN ('REQUESTED','PROVISIONING','READY','ACTIVE','COMPLETED','EXPIRED',"
            "'FAILED','TERMINATING','TERMINATED')",
            name="status",
        ),
        # No máximo uma sessão executável por aluno e release (docs/08 §2, G-12).
        Index(
            "uq_lab_sessions_one_active",
            "user_id",
            "release_id",
            unique=True,
            postgresql_where=text(f"status IN ({_active_sql})"),
            sqlite_where=text(f"status IN ({_active_sql})"),
        ),
        Index("ix_lab_sessions_user_status", "user_id", "status"),
        Index("ix_lab_sessions_expires_status", "expires_at", "status"),
        Index("ix_lab_sessions_ready_at", "ready_at"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    release_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_releases.id"))
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_variants.id"))
    status: Mapped[str] = mapped_column(String(16))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_fingerprint: Mapped[str] = mapped_column(String(80))
    expires_at: Mapped[datetime] = mapped_column(TZ)
    last_error_code: Mapped[str | None] = mapped_column(String(64))
    correlation_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ)
    updated_at: Mapped[datetime] = mapped_column(TZ)
    version_num: Mapped[int] = mapped_column(Integer, default=1)
    # Tentativa acadêmica dona do progresso (ADR-005); a sessão é só o runtime efêmero.
    attempt_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lab_attempts.id"))
    # Indicadores (ADR-011): quando ficou pronta e quanto levou desde a solicitação; renovações feitas.
    ready_at: Mapped[datetime | None] = mapped_column(TZ)
    provision_ms: Mapped[int | None] = mapped_column(Integer)
    renewals: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    __mapper_args__ = {"version_id_col": version_num}


class RuntimeInstance(Base):
    __tablename__ = "runtime_instances"
    __table_args__ = (UniqueConstraint("external_ref", name="uq_runtime_instances_external_ref"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_sessions.id"), unique=True)
    provider: Mapped[str] = mapped_column(String(32))
    external_ref: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(TZ)
    terminated_at: Mapped[datetime | None] = mapped_column(TZ)
    # Destino interno da aplicação (rede da sessão). Só o gateway consome; nunca vai ao navegador.
    endpoint_host: Mapped[str | None] = mapped_column(String(255))
    endpoint_port: Mapped[int | None] = mapped_column(Integer)


class Job(Base):
    """Fila transacional no PostgreSQL (ADR-007): comandos de provisionamento e término."""

    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("kind IN ('PROVISION','TERMINATE','EVALUATE')", name="kind"),
        CheckConstraint("status IN ('queued','running','succeeded','dead')", name="status"),
        # Deduplicação: no máximo um job pendente por (tipo, sessão).
        Index(
            "uq_jobs_pending_per_session",
            "kind",
            "session_id",
            unique=True,
            postgresql_where=text("status IN ('queued','running')"),
            sqlite_where=text("status IN ('queued','running')"),
        ),
        Index("ix_jobs_status_run_at", "status", "run_at"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(16))
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_sessions.id"))
    status: Mapped[str] = mapped_column(String(16))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer)
    run_at: Mapped[datetime] = mapped_column(TZ)
    deadline_at: Mapped[datetime | None] = mapped_column(TZ)
    lease_owner: Mapped[str | None] = mapped_column(String(128))
    lease_expires_at: Mapped[datetime | None] = mapped_column(TZ)
    last_error: Mapped[str | None] = mapped_column(String(500))
    correlation_id: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ)
    updated_at: Mapped[datetime] = mapped_column(TZ)


class LabAttempt(Base):
    """Tentativa de resolução do laboratório (ADR-005): durável e dona do progresso."""

    __tablename__ = "lab_attempts"
    __table_args__ = (
        CheckConstraint("status IN ('IN_PROGRESS','COMPLETED')", name="status"),
        Index(
            "uq_lab_attempts_one_open",
            "user_id",
            "release_id",
            "variant_id",
            unique=True,
            postgresql_where=text("status = 'IN_PROGRESS'"),
            sqlite_where=text("status = 'IN_PROGRESS'"),
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    release_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_releases.id"))
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_variants.id"))
    status: Mapped[str] = mapped_column(String(16))
    score: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(TZ)
    completed_at: Mapped[datetime | None] = mapped_column(TZ)


class StepProgress(Base):
    __tablename__ = "step_progress"
    __table_args__ = (
        UniqueConstraint("attempt_id", "step_id", name="uq_step_progress_attempt_step"),
        CheckConstraint("status IN ('LOCKED','AVAILABLE','PASSED')", name="status"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_attempts.id"))
    step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_steps.id"))
    status: Mapped[str] = mapped_column(String(16))
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)
    submissions: Mapped[int] = mapped_column(Integer, default=0)
    passed_at: Mapped[datetime | None] = mapped_column(TZ)
    updated_at: Mapped[datetime] = mapped_column(TZ)


class StepSubmission(Base):
    """Submissão imutável de etapa + execução da validação (ADR-005: step_submissions/validation_runs)."""

    __tablename__ = "step_submissions"
    __table_args__ = (
        UniqueConstraint("session_id", "idempotency_key", name="uq_step_submissions_session_idem"),
        CheckConstraint("status IN ('QUEUED','RUNNING','PASSED','FAILED','ERROR')", name="status"),
        # No máximo uma avaliação pendente por sessão (docs/10 §4, serialização do MVP).
        Index(
            "uq_step_submissions_one_pending",
            "session_id",
            unique=True,
            postgresql_where=text("status IN ('QUEUED','RUNNING')"),
            sqlite_where=text("status IN ('QUEUED','RUNNING')"),
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_attempts.id"))
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_sessions.id"))
    step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_steps.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_fingerprint: Mapped[str] = mapped_column(String(80))
    validator_ref: Mapped[str] = mapped_column(String(200))
    suite_digest: Mapped[str] = mapped_column(String(80))
    # Resposta textual do aluno (quando a etapa pede), já normalizada e truncada; nunca segredo.
    answer: Mapped[str | None] = mapped_column(String(500))
    snapshot_digest: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(16))
    # Resultado por critério (`criterion_results`), só com o que pode ser divulgado ao aluno.
    criteria: Mapped[list[dict[str, Any]]] = mapped_column(JsonType, default=list)
    feedback: Mapped[str | None] = mapped_column(Text)
    error_code: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TZ)
    started_at: Mapped[datetime | None] = mapped_column(TZ)
    finished_at: Mapped[datetime | None] = mapped_column(TZ)


class HintUsage(Base):
    """Uso de dicas, append-only. OPEN-04 (PO, 2026-11-12): sem penalidade; registrado para relatórios."""

    __tablename__ = "hint_usages"
    __table_args__ = (
        UniqueConstraint("attempt_id", "step_id", "level", name="uq_hint_usages_attempt_step_level"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_attempts.id"))
    step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lab_steps.id"))
    level: Mapped[int] = mapped_column(Integer)
    revealed_at: Mapped[datetime] = mapped_column(TZ)


class AuditEvent(Base):
    """Trilha append-only lógica; sem segredos e com PII mínima (apenas ids)."""

    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_events_occurred_at", "occurred_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Ordem total de inserção (eventos na mesma transação podem ter o mesmo occurred_at).
    seq: Mapped[int] = mapped_column(BigInteger, Identity(always=True), unique=True)
    actor_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    resource_kind: Mapped[str] = mapped_column(String(32))
    resource_id: Mapped[str] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(TZ)
    trace_id: Mapped[str | None] = mapped_column(String(64))
    event_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JsonType, default=dict)
