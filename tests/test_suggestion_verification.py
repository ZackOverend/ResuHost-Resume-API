from uuid import UUID

from app import schemas
from app.resume_documents import source_hash
from app.suggestion_verification import verify_suggestion


ENTRY_ID = UUID(int=1)
TEXT = "Reduced processing time by 30%."


def document():
    return schemas.ResumeDocument(
        profile_version="a" * 64,
        contact=schemas.ResumeDocumentContact(
            name="Ada", email="ada@example.com"
        ),
        sections=[
            schemas.ResumeDocumentSection(
                kind="experience",
                label="Experience",
                entries=[
                    schemas.ResumeDocumentEntry(
                        source_entry_id=ENTRY_ID,
                        heading="Engineer",
                        bullets=[
                            schemas.ResumeDocumentBullet(
                                text=TEXT,
                                source_section="experience",
                                source_entry_id=ENTRY_ID,
                                source_index=0,
                                source_hash=source_hash(TEXT),
                            )
                        ],
                    )
                ],
            )
        ],
    )


def candidate(**changes):
    values = {
        "id": UUID(int=2),
        "section": "experience",
        "entry_id": ENTRY_ID,
        "source_index": 0,
        "source_hash": source_hash(TEXT),
        "original_text": TEXT,
        "proposed_text": "Cut processing time by 30% through pipeline optimization.",
        "reason": "Uses a more direct action verb.",
        "matched_requirements": ["performance optimization"],
    }
    values.update(changes)
    return schemas.TailoringSuggestionCandidate(**values)


def test_valid_suggestion_passes_verification():
    result = verify_suggestion(candidate(), document())

    assert result.verification.status == "pass"
    assert result.verification.issues == []


def test_new_metric_fails_verification():
    result = verify_suggestion(
        candidate(proposed_text="Cut processing time by 50%."), document()
    )

    assert result.verification.status == "fail"
    assert "introduced_metric" in {
        issue.code for issue in result.verification.issues
    }


def test_stale_hash_and_wrong_entry_assignment_fail_verification():
    result = verify_suggestion(
        candidate(
            section="project",
            source_hash=source_hash("Old source text"),
        ),
        document(),
    )

    assert result.verification.status == "fail"
    assert {issue.code for issue in result.verification.issues} >= {
        "wrong_section",
        "stale_source_hash",
    }
