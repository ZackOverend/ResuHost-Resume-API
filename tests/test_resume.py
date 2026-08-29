from types import SimpleNamespace
from uuid import UUID

from app.api.resume import build_user_data


def record(record_id: int, *, archived: bool = False, order: int = 0, **fields):
    return SimpleNamespace(
        id=UUID(int=record_id),
        is_archived=archived,
        sort_order=order,
        **fields,
    )


def test_base_resume_uses_active_ordered_profile_records():
    earlier = record(
        1,
        order=0,
        company="Earlier",
        role="Engineer",
        location=None,
        start_date="2025-01",
        end_date=None,
        is_current=True,
        bullets=[],
    )
    later = record(
        2,
        order=1,
        company="Later",
        role="Engineer",
        location=None,
        start_date="2024-01",
        end_date="2024-12",
        is_current=False,
        bullets=[],
    )
    archived = record(
        3,
        archived=True,
        company="Archived",
        role="Engineer",
        location=None,
        start_date=None,
        end_date=None,
        is_current=False,
        bullets=[],
    )
    user = SimpleNamespace(
        name="Ada",
        email="ada@example.com",
        phone=None,
        linkedin=None,
        website=None,
        experiences=[later, archived, earlier],
        education=[],
        projects=[],
        activities=[],
        skill_categories=[],
    )

    data = build_user_data(user)

    assert [item["company"] for item in data["experiences"]] == ["Earlier", "Later"]
    assert data["experiences"][0]["end_date"] == "Present"
