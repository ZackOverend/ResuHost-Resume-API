from types import SimpleNamespace
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.api.profile import _ordered, _profile_version
from app.schemas import (
    ActivityPatch,
    EducationPatch,
    ExperiencePatch,
    ProfileContactPatch,
    ProfileReorder,
    ProjectPatch,
    SkillCategoryPatch,
)


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


def test_contact_patch_tracks_only_supplied_fields():
    patch = ProfileContactPatch(phone="555-0100")

    assert patch.model_dump(exclude_unset=True) == {"phone": "555-0100"}


def test_experience_patch_tracks_only_supplied_fields():
    patch = ExperiencePatch(role="Staff Engineer")

    assert patch.model_dump(exclude_unset=True) == {"role": "Staff Engineer"}


def test_education_patch_tracks_only_supplied_fields():
    patch = EducationPatch(degree="BSc")

    assert patch.model_dump(exclude_unset=True) == {"degree": "BSc"}


def test_project_patch_tracks_only_supplied_fields():
    patch = ProjectPatch(subtitle="Compiler project")

    assert patch.model_dump(exclude_unset=True) == {"subtitle": "Compiler project"}


def test_activity_patch_tracks_only_supplied_fields():
    patch = ActivityPatch(role="Treasurer")

    assert patch.model_dump(exclude_unset=True) == {"role": "Treasurer"}


def test_skill_category_patch_tracks_only_supplied_fields():
    patch = SkillCategoryPatch(skills=["Python", "PostgreSQL"])

    assert patch.model_dump(exclude_unset=True) == {
        "skills": ["Python", "PostgreSQL"]
    }


def test_reorder_rejects_duplicate_ids():
    record_id = UUID(int=1)

    with pytest.raises(ValidationError):
        ProfileReorder(ids=[record_id, record_id])
