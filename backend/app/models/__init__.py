"""Domain models for core OKR entities."""
from __future__ import annotations

import enum
from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID as UUIDType, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TimestampMixin:
    """Mixin providing timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Tenant(Base, TimestampMixin):
    """Tenant represents a company account."""

    __tablename__ = "tenants"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    workspaces: Mapped[List["Workspace"]] = relationship("Workspace", back_populates="tenant")
    users: Mapped[List["User"]] = relationship("User", back_populates="tenant")


class TenantScopedMixin:
    """Mixin for entities that belong to a tenant."""

    tenant_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)


class Workspace(Base, TimestampMixin, TenantScopedMixin):
    """Hierarchical workspace within a tenant."""

    __tablename__ = "workspaces"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[UUIDType]] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))

    parent: Mapped[Optional["Workspace"]] = relationship(
        "Workspace", remote_side="Workspace.id", backref="children"
    )
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="workspaces")
    members: Mapped[List["User"]] = relationship("User", back_populates="workspace")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_workspace_name_per_tenant"),
        Index("ix_workspaces_tenant", "tenant_id"),
    )


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(Base, TimestampMixin, TenantScopedMixin):
    """A user provisioned via Azure AD or SCIM."""

    __tablename__ = "users"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    workspace_id: Mapped[Optional[UUIDType]] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    manager_id: Mapped[Optional[UUIDType]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    workspace: Mapped[Optional["Workspace"]] = relationship("Workspace", back_populates="members")
    manager: Mapped[Optional["User"]] = relationship(
        "User", remote_side="User.id", backref="direct_reports"
    )
    objectives: Mapped[List["Objective"]] = relationship("Objective", back_populates="owner")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_user_email_per_tenant"),
        Index("ix_users_tenant", "tenant_id"),
        Index("ix_users_workspace", "workspace_id"),
    )


class ObjectiveStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Objective(Base, TimestampMixin, TenantScopedMixin):
    """Represents an Objective in the OKR framework."""

    __tablename__ = "objectives"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ObjectiveStatus] = mapped_column(
        Enum(ObjectiveStatus), default=ObjectiveStatus.DRAFT, nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    owner_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="objectives")
    workspace: Mapped["Workspace"] = relationship("Workspace")
    key_results: Mapped[List["KeyResult"]] = relationship(
        "KeyResult", back_populates="objective", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("start_date <= due_date", name="ck_objectives_dates"),
        Index("ix_objectives_tenant", "tenant_id"),
        Index("ix_objectives_workspace", "workspace_id"),
    )


class KeyResultType(str, enum.Enum):
    PERCENTAGE = "percentage"
    ABSOLUTE = "absolute"
    BINARY = "binary"
    KPI = "kpi"


class KeyResult(Base, TimestampMixin, TenantScopedMixin):
    """Represents progress measurement for an objective."""

    __tablename__ = "key_results"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    objective_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objectives.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    metric_type: Mapped[KeyResultType] = mapped_column(Enum(KeyResultType), nullable=False)
    target_value: Mapped[float] = mapped_column(nullable=False)
    current_value: Mapped[float] = mapped_column(nullable=False, default=0.0)
    unit: Mapped[Optional[str]] = mapped_column(String(50))
    progress: Mapped[float] = mapped_column(nullable=False, default=0.0)
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    objective: Mapped["Objective"] = relationship("Objective", back_populates="key_results")
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="key_result", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 1", name="ck_key_results_progress_range"),
        Index("ix_key_results_objective", "objective_id"),
        Index("ix_key_results_tenant", "tenant_id"),
    )


class Attachment(Base, TimestampMixin, TenantScopedMixin):
    """Metadata for files stored on the local filesystem."""

    __tablename__ = "attachments"

    id: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    key_result_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("key_results.id")
    )
    objective_id: Mapped[Optional[UUIDType]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("objectives.id")
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)

    key_result: Mapped[Optional["KeyResult"]] = relationship("KeyResult", back_populates="attachments")
    objective: Mapped[Optional["Objective"]] = relationship("Objective")

    __table_args__ = (Index("ix_attachments_tenant", "tenant_id"),)


def _register_tenant_rls(table_name: str) -> None:
    policy_name = f"{table_name}_tenant_isolation"
    clause = (
        "current_setting('app.current_tenant', true) IS NOT NULL "
        "AND tenant_id = current_setting('app.current_tenant')::uuid"
    )
    table = Base.metadata.tables[table_name]

    event.listen(table, "after_create", event.DDL(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"))
    event.listen(table, "after_create", event.DDL(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY"))
    event.listen(
        table,
        "after_create",
        event.DDL(
            f"CREATE POLICY {policy_name} ON {table_name} USING ({clause}) WITH CHECK ({clause})"
        ),
    )
    event.listen(
        table,
        "before_drop",
        event.DDL(f"DROP POLICY IF EXISTS {policy_name} ON {table_name}"),
    )


for _table_name in ("workspaces", "users", "objectives", "key_results", "attachments"):
    _register_tenant_rls(_table_name)


__all__ = [
    "Attachment",
    "KeyResult",
    "KeyResultType",
    "Objective",
    "ObjectiveStatus",
    "Tenant",
    "TenantScopedMixin",
    "User",
    "UserStatus",
    "Workspace",
]
