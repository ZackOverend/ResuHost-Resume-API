"""Add current-state flags to date-based profile records.

Revision ID: 0003_current_profile_records
Revises: 0002_master_profile_foundation
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_current_profile_records"
down_revision: Union[str, Sequence[str], None] = "0002_master_profile_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DATE_RANGE_TABLES = ("education", "experiences", "projects", "activities")


def upgrade() -> None:
    for table_name in DATE_RANGE_TABLES:
        op.add_column(
            table_name,
            sa.Column(
                "is_current",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
        )


def downgrade() -> None:
    for table_name in reversed(DATE_RANGE_TABLES):
        op.drop_column(table_name, "is_current")
