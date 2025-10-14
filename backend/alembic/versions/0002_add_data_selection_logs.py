"""Add data selection journal table."""
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_add_data_selection_logs"
down_revision: str | None = "0001_initial_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "data_selection_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("connector_type", sa.String(length=100), nullable=False),
        sa.Column("operation", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("status", sa.Enum("running", "success", "fail_safe", "failure", name="dataselectionstatus"), nullable=False, server_default="running"),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("fail_safe_triggered", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("data_selection_logs")
    op.execute("DROP TYPE IF EXISTS dataselectionstatus")
