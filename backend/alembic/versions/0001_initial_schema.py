"""Initial database schema for OKRio core domains."""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _enable_rls(table: str) -> None:
    policy = f"{table}_tenant_isolation"
    clause = "current_setting('app.current_tenant', true) IS NOT NULL AND tenant_id = current_setting('app.current_tenant')::uuid"
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY {policy} ON {table} USING ({clause}) WITH CHECK ({clause})"
    )


def _disable_rls(table: str) -> None:
    policy = f"{table}_tenant_isolation"
    op.execute(f"DROP POLICY IF EXISTS {policy} ON {table}")


def upgrade() -> None:  # noqa: D401
    """Apply the initial schema."""

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_tenants_name"),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )

    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["workspaces.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_workspace_name_per_tenant"),
    )
    op.create_index("ix_workspaces_tenant", "workspaces", ["tenant_id"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("job_title", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_user_email_per_tenant"),
    )
    op.create_index("ix_users_tenant", "users", ["tenant_id"])
    op.create_index("ix_users_workspace", "users", ["workspace_id"])

    op.create_table(
        "objectives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.CheckConstraint("start_date <= due_date", name="ck_objectives_dates"),
    )
    op.create_index("ix_objectives_tenant", "objectives", ["tenant_id"])
    op.create_index("ix_objectives_workspace", "objectives", ["workspace_id"])

    op.create_table(
        "key_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("objective_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("metric_type", sa.String(length=50), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=False),
        sa.Column("current_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["objective_id"], ["objectives.id"], ondelete="CASCADE"),
        sa.CheckConstraint("progress >= 0 AND progress <= 1", name="ck_key_results_progress_range"),
    )
    op.create_index("ix_key_results_objective", "key_results", ["objective_id"])
    op.create_index("ix_key_results_tenant", "key_results", ["tenant_id"])

    op.create_table(
        "attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key_result_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("objective_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["key_result_id"], ["key_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["objective_id"], ["objectives.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_attachments_tenant", "attachments", ["tenant_id"])

    for table in ("workspaces", "users", "objectives", "key_results", "attachments"):
        _enable_rls(table)


def downgrade() -> None:  # noqa: D401
    """Drop the initial schema."""

    for table in ("attachments", "key_results", "objectives", "users", "workspaces"):
        _disable_rls(table)

    op.drop_index("ix_attachments_tenant", table_name="attachments")
    op.drop_table("attachments")

    op.drop_index("ix_key_results_tenant", table_name="key_results")
    op.drop_index("ix_key_results_objective", table_name="key_results")
    op.drop_table("key_results")

    op.drop_index("ix_objectives_workspace", table_name="objectives")
    op.drop_index("ix_objectives_tenant", table_name="objectives")
    op.drop_table("objectives")

    op.drop_index("ix_users_workspace", table_name="users")
    op.drop_index("ix_users_tenant", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_workspaces_tenant", table_name="workspaces")
    op.drop_table("workspaces")

    op.drop_table("tenants")
