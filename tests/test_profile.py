from types import SimpleNamespace
from uuid import UUID

from app.api.profile import _ordered, _profile_version


def test_profile_version_is_deterministic_for_equivalent_data():
    first = {"contact": {"name": "Ada"}, "experiences": [{"role": "Engineer"}]}
    second = {"experiences": [{"role": "Engineer"}], "contact": {"name": "Ada"}}

    assert _profile_version(first) == _profile_version(second)
    assert len(_profile_version(first)) == 64


def test_profile_version_changes_with_profile_content():
    original = {"contact": {"name": "Ada"}}
    changed = {"contact": {"name": "Grace"}}

    assert _profile_version(original) != _profile_version(changed)


def test_profile_records_are_ordered_with_archived_records_last():
    records = [
        SimpleNamespace(id=UUID(int=3), is_archived=True, sort_order=0),
        SimpleNamespace(id=UUID(int=2), is_archived=False, sort_order=2),
        SimpleNamespace(id=UUID(int=1), is_archived=False, sort_order=1),
    ]

    assert [record.id.int for record in _ordered(records)] == [1, 2, 3]
