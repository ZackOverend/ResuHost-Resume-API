"""Create the initial ResuHost schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("linkedin", sa.String(), nullable=True),
        sa.Column("website", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    for table_name, columns in (
        (
            "education",
            [
                sa.Column("institution", sa.String(), nullable=False),
                sa.Column("degree", sa.String(), nullable=True),
                sa.Column("location", sa.String(), nullable=True),
                sa.Column("start_date", sa.String(), nullable=True),
                sa.Column("end_date", sa.String(), nullable=True),
                sa.Column("notes", postgresql.ARRAY(sa.String()), nullable=True),
            ],
        ),
        (
            "experiences",
            [
                sa.Column("company", sa.String(), nullable=False),
                sa.Column("role", sa.String(), nullable=False),
                sa.Column("location", sa.String(), nullable=True),
                sa.Column("start_date", sa.String(), nullable=True),
                sa.Column("end_date", sa.String(), nullable=True),
                sa.Column("bullets", postgresql.ARRAY(sa.String()), nullable=True),
            ],
        ),
        (
            "projects",
            [
                sa.Column("name", sa.String(), nullable=False),
                sa.Column("subtitle", sa.String(), nullable=True),
                sa.Column("start_date", sa.String(), nullable=True),
                sa.Column("end_date", sa.String(), nullable=True),
                sa.Column("bullets", postgresql.ARRAY(sa.String()), nullable=True),
            ],
        ),
        (
            "activities",
            [
                sa.Column("role", sa.String(), nullable=False),
                sa.Column("organization", sa.String(), nullable=False),
                sa.Column("start_date", sa.String(), nullable=True),
                sa.Column("end_date", sa.String(), nullable=True),
                sa.Column("bullets", postgresql.ARRAY(sa.String()), nullable=True),
            ],
        ),
        (
            "skill_categories",
            [
                sa.Column("name", sa.String(), nullable=False),
                sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=True),
            ],
        ),
    ):
        op.create_table(
            table_name,
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            *columns,
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f(f"ix_{table_name}_id"), table_name, ["id"], unique=False)

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resumes_id"), "resumes", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resumes_id"), table_name="resumes")
    op.drop_table("resumes")
    for table_name in (
        "skill_categories",
        "activities",
        "projects",
        "experiences",
        "education",
    ):
        op.drop_index(op.f(f"ix_{table_name}_id"), table_name=table_name)
        op.drop_table(table_name)
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
