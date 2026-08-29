"""Upgrade the database while safely adopting pre-Alembic ResuHost schemas."""

from enum import Enum

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database import engine


INITIAL_REVISION = "0001_initial"
MANAGED_TABLES = frozenset(
    {
        "users",
        "education",
        "experiences",
        "projects",
        "activities",
        "skill_categories",
        "resumes",
    }
)


class DatabaseState(str, Enum):
    NEW = "new"
    LEGACY_COMPLETE = "legacy_complete"
    ALEMBIC_MANAGED = "alembic_managed"
    LEGACY_PARTIAL = "legacy_partial"


def classify_database_tables(tables: set[str]) -> DatabaseState:
    if "alembic_version" in tables:
        return DatabaseState.ALEMBIC_MANAGED

    present_managed_tables = tables & MANAGED_TABLES
    if not present_managed_tables:
        return DatabaseState.NEW
    if MANAGED_TABLES <= tables:
        return DatabaseState.LEGACY_COMPLETE
    return DatabaseState.LEGACY_PARTIAL


def migrate() -> None:
    config = Config("alembic.ini")
    tables = set(inspect(engine).get_table_names())
    state = classify_database_tables(tables)

    if state is DatabaseState.LEGACY_PARTIAL:
        missing = ", ".join(sorted(MANAGED_TABLES - tables))
        raise RuntimeError(
            "Database contains a partial pre-Alembic ResuHost schema. "
            f"Missing managed tables: {missing}. Resolve it before migrating."
        )

    if state is DatabaseState.LEGACY_COMPLETE:
        print("Adopting existing ResuHost schema at revision 0001_initial.")
        command.stamp(config, INITIAL_REVISION)

    command.upgrade(config, "head")


if __name__ == "__main__":
    migrate()
