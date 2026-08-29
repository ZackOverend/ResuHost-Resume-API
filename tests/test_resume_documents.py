from types import SimpleNamespace
from uuid import UUID

from app.resume_documents import build_resume_document, source_hash


def test_source_hash_is_deterministic_and_namespaced():
    assert source_hash("Built a service") == source_hash("Built a service")
    assert source_hash("Built a service").startswith("sha256:")
    assert source_hash("Built a service") != source_hash("Built two services")


def test_resume_document_preserves_bullet_source_identity():
    experience_id = UUID(int=1)
    experience = SimpleNamespace(
        id=experience_id,
        is_archived=False,
        sort_order=0,
        role="Engineer",
        company="Acme",
        location=None,
        start_date="2025-01",
        end_date=None,
        is_current=True,
        bullets=["Reduced processing time by 30%."],
    )
    user = SimpleNamespace(
        name="Ada",
        email="ada@example.com",
        phone=None,
        linkedin=None,
        website=None,
        experiences=[experience],
        projects=[],
        education=[],
        activities=[],
        skill_categories=[],
    )

    document = build_resume_document(user, "a" * 64)
    bullet = document.sections[0].entries[0].bullets[0]

    assert document.profile_version == "a" * 64
    assert bullet.source_section == "experience"
    assert bullet.source_entry_id == experience_id
    assert bullet.source_index == 0
    assert bullet.source_hash == source_hash(bullet.text)
