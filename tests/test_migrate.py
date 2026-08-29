import pytest

from scripts.migrate import DatabaseState, MANAGED_TABLES, classify_database_tables


@pytest.mark.parametrize(
    ("tables", "expected"),
    [
        (set(), DatabaseState.NEW),
        ({"unrelated_table"}, DatabaseState.NEW),
        ({"alembic_version"}, DatabaseState.ALEMBIC_MANAGED),
        (set(MANAGED_TABLES), DatabaseState.LEGACY_COMPLETE),
        ({"users", "experiences"}, DatabaseState.LEGACY_PARTIAL),
    ],
)
def test_classify_database_tables(tables, expected):
    assert classify_database_tables(tables) is expected
