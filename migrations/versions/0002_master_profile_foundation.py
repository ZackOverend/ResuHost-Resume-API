"""Add master profile lifecycle metadata.

Revision ID: 0002_master_profile_foundation
Revises: 0001_initial
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_master_profile_foundation"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PROFILE_TABLES = (
    "education",
    "experiences",
    "projects",
    "activities",
    "skill_categories",
)


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "users", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True)
    )

    for table_name in PROFILE_TABLES:
        op.add_column(
            table_name,
            sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        )
        op.add_column(
            table_name,
            sa.Column(
                "is_archived",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
        )
        op.add_column(
            table_name,
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )
        op.add_column(
            table_name,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )
        op.add_column(
            table_name,
            sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.add_column(
            table_name,
            sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index(
            f"ix_{table_name}_profile_order",
            table_name,
            ["user_id", "is_archived", "sort_order"],
            unique=False,
        )


def downgrade() -> None:
    for table_name in reversed(PROFILE_TABLES):
        op.drop_index(f"ix_{table_name}_profile_order", table_name=table_name)
        for column_name in (
            "verified_at",
            "archived_at",
            "updated_at",
            "created_at",
            "is_archived",
            "sort_order",
        ):
            op.drop_column(table_name, column_name)

    op.drop_column("users", "verified_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
