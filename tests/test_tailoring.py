from uuid import UUID

from app import schemas
from app.resume_documents import source_hash
from app.tailoring import bullet_refs, resolve_proposals, tailoring_prompt


EXPERIENCE_ID = UUID(int=1)
PROJECT_ID = UUID(int=2)
FIRST = "Reduced processing time by 30%."
SECOND = "Maintained the billing service."
PROJECT = "Built a Python CLI for log analysis."


def bullet(section, entry_id, index, text):
    return schemas.ResumeDocumentBullet(
        text=text,
        source_section=section,
        source_entry_id=entry_id,
        source_index=index,
        source_hash=source_hash(text),
    )


def document():
    return schemas.ResumeDocument(
        profile_version="a" * 64,
        contact=schemas.ResumeDocumentContact(name="Ada", email="ada@example.com"),
        sections=[
            schemas.ResumeDocumentSection(
                kind="experience",
                label="Experience",
                entries=[
                    schemas.ResumeDocumentEntry(
                        source_entry_id=EXPERIENCE_ID,
                        heading="Engineer",
                        subheading="Acme",
                        start_date="2020-01",
                        is_current=True,
                        bullets=[
                            bullet("experience", EXPERIENCE_ID, 0, FIRST),
                            # Index 1 was a blank bullet skipped by the document builder.
                            bullet("experience", EXPERIENCE_ID, 2, SECOND),
                        ],
                    )
                ],
            ),
            schemas.ResumeDocumentSection(
                kind="project",
                label="Projects",
                entries=[
                    schemas.ResumeDocumentEntry(
                        source_entry_id=PROJECT_ID,
                        heading="Log Tool",
                        bullets=[bullet("project", PROJECT_ID, 0, PROJECT)],
                    )
                ],
            ),
        ],
    )


def proposal(ref, text, reason="Matches the role."):
    return schemas.TailoringProposal(
        bullet_ref=ref,
        proposed_text=text,
        reason=reason,
        matched_requirements=["performance"],
    )


def test_bullet_refs_are_sequential_in_document_order():
    refs = bullet_refs(document())

    assert list(refs) == ["b1", "b2", "b3"]
    assert refs["b2"].text == SECOND
    assert refs["b2"].source_index == 2
    assert refs["b3"].source_section == "project"


def test_prompt_labels_bullets_without_exposing_hashes_or_ids():
    prompt = tailoring_prompt("Seeking a Python engineer.", document())

    assert "Seeking a Python engineer." in prompt
    assert f"b1: {FIRST}" in prompt
    assert f"b3: {PROJECT}" in prompt
    assert "Engineer — Acme" in prompt
    assert "sha256" not in prompt
    assert str(EXPERIENCE_ID) not in prompt


def test_proposals_resolve_to_server_owned_source_identity():
    [suggestion] = resolve_proposals(
        [proposal("b2", "Owned the billing service end to end.")], document()
    )

    assert suggestion.section == "experience"
    assert suggestion.entry_id == EXPERIENCE_ID
    assert suggestion.source_index == 2
    assert suggestion.source_hash == source_hash(SECOND)
    assert suggestion.original_text == SECOND
    assert suggestion.verification.status == "pass"


def test_each_suggestion_gets_a_unique_server_id():
    suggestions = resolve_proposals(
        [proposal("b1", "Cut processing time by 30%."), proposal("b1", "Sped up processing by 30%.")],
        document(),
    )

    assert len({suggestion.id for suggestion in suggestions}) == 2


def test_refs_are_matched_leniently():
    [suggestion] = resolve_proposals([proposal(" B3 ", "Built a Python log-analysis CLI.")], document())

    assert suggestion.entry_id == PROJECT_ID


def test_unknown_refs_and_unchanged_text_are_discarded():
    suggestions = resolve_proposals(
        [
            proposal("b9", "Invented bullet."),
            proposal("b1", f"  {FIRST}  "),
            proposal("b2", "Owned the billing service."),
        ],
        document(),
    )

    assert [suggestion.source_index for suggestion in suggestions] == [2]


def test_failing_proposals_are_kept_with_verification_issues():
    [suggestion] = resolve_proposals([proposal("b1", "Reduced processing time by 90%.")], document())

    assert suggestion.verification.status == "fail"
    assert suggestion.verification.issues[0].code == "introduced_metric"
