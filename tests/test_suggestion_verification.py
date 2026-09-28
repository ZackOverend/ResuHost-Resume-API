from uuid import UUID

import pytest

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
                        subheading="Acme",
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


def issue_codes(proposed_text):
    result = verify_suggestion(candidate(proposed_text=proposed_text), document())
    return {issue.code for issue in result.verification.issues}, result


@pytest.mark.parametrize(
    ("proposed_text", "term"),
    [
        ("Reduced processing time by 30% using Kubernetes.", "Kubernetes"),
        ("Reduced AWS processing time by 30%.", "AWS"),
        ("Reduced processing time by 30% with Node.js.", "Node.js"),
        ("Reduced processing time by 30% as Senior Engineer.", "Senior"),
        ("Reduced processing time by 30% in March.", "March"),
    ],
)
def test_new_named_terms_fail_verification(proposed_text, term):
    codes, result = issue_codes(proposed_text)

    assert codes == {"introduced_named_term"}
    assert f"{term}." in result.verification.issues[0].message


@pytest.mark.parametrize(
    "proposed_text",
    [
        "Reduced Acme processing time by 30%.",
        "Engineer who reduced processing time by 30%.",
        "Streamlined workflows. Reduced processing time by 30%.",
    ],
)
def test_terms_from_the_source_entry_pass_verification(proposed_text):
    codes, _ = issue_codes(proposed_text)

    assert codes == set()


def test_new_credential_language_fails_verification():
    codes, _ = issue_codes("As a certified engineer, reduced processing time by 30%.")

    assert codes == {"introduced_credential"}
