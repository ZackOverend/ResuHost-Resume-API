"""Add non-destructive tailoring runs and resume variants.

Revision ID: 0004_resume_variants
Revises: 0003_current_profile_records
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0004_resume_variants"
down_revision: Union[str, Sequence[str], None] = "0003_current_profile_records"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tailoring_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_version", sa.String(length=64), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="pending", nullable=False),
        sa.Column("suggestions", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'completed', 'failed')",
            name="ck_tailoring_runs_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tailoring_runs_id", "tailoring_runs", ["id"])
    op.create_index(
        "ix_tailoring_runs_user_created",
        "tailoring_runs",
        ["user_id", "created_at"],
    )

    op.create_table(
        "resume_variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "tailoring_run_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("profile_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(), server_default="draft", nullable=False),
        sa.Column("document", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'approved')",
            name="ck_resume_variants_status",
        ),
        sa.ForeignKeyConstraint(["tailoring_run_id"], ["tailoring_runs.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_variants_id", "resume_variants", ["id"])
    op.create_index(
        "ix_resume_variants_user_created",
        "resume_variants",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_resume_variants_user_created", table_name="resume_variants")
    op.drop_index("ix_resume_variants_id", table_name="resume_variants")
    op.drop_table("resume_variants")
    op.drop_index("ix_tailoring_runs_user_created", table_name="tailoring_runs")
    op.drop_index("ix_tailoring_runs_id", table_name="tailoring_runs")
    op.drop_table("tailoring_runs")
