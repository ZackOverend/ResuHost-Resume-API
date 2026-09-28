from uuid import UUID

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import schemas
from app.resume_documents import source_hash
from app.resume_variants import create_variant_document


ENTRY_ID = UUID(int=1)
SUGGESTION_ID = UUID(int=2)
SOURCE_TEXT = "Reduced processing time by 30%."


def source_document():
    return schemas.ResumeDocument(
        profile_version="a" * 64,
        contact=schemas.ResumeDocumentContact(name="Ada", email="ada@example.com"),
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
                                text=SOURCE_TEXT,
                                source_section="experience",
                                source_entry_id=ENTRY_ID,
                                source_index=0,
                                source_hash=source_hash(SOURCE_TEXT),
                            )
                        ],
                    )
                ],
            )
        ],
    )


def suggestion(
    proposed_text="Cut processing time by 30% through optimization.",
    suggestion_id=SUGGESTION_ID,
):
    return schemas.TailoringSuggestion(
        id=suggestion_id,
        section="experience",
        entry_id=ENTRY_ID,
        source_index=0,
        source_hash=source_hash(SOURCE_TEXT),
        original_text=SOURCE_TEXT,
        proposed_text=proposed_text,
        reason="Uses a direct action verb.",
        matched_requirements=["optimization"],
        verification=schemas.SuggestionVerification(status="pass"),
    )


def decision(action="accept", edited_text=None, suggestion_id=SUGGESTION_ID):
    return schemas.VariantSuggestionDecision(
        suggestion_id=suggestion_id,
        action=action,
        edited_text=edited_text,
    )


def test_accepting_suggestion_changes_only_variant_copy():
    source = source_document()

    variant = create_variant_document(source, [suggestion()], [decision()])

    assert source.sections[0].entries[0].bullets[0].text == SOURCE_TEXT
    assert variant.sections[0].entries[0].bullets[0].text.startswith("Cut processing")


def test_rejecting_suggestion_preserves_original_text():
    variant = create_variant_document(
        source_document(), [suggestion()], [decision(action="reject")]
    )

    assert variant.sections[0].entries[0].bullets[0].text == SOURCE_TEXT


def test_edited_suggestion_is_verified_again():
    with pytest.raises(HTTPException) as error:
        create_variant_document(
            source_document(),
            [suggestion()],
            [decision(action="edit", edited_text="Reduced processing time by 90%.")],
        )

    assert error.value.status_code == 422


def test_variant_rejects_two_changes_to_the_same_bullet():
    other_id = UUID(int=3)
    suggestions = [suggestion(), suggestion("Sped up processing by 30%.", suggestion_id=other_id)]

    with pytest.raises(HTTPException) as error:
        create_variant_document(
            source_document(),
            suggestions,
            [decision(), decision(suggestion_id=other_id)],
        )

    assert error.value.status_code == 422


def test_rejected_alternative_does_not_conflict():
    other_id = UUID(int=3)
    suggestions = [suggestion(), suggestion("Sped up processing by 30%.", suggestion_id=other_id)]

    variant = create_variant_document(
        source_document(),
        suggestions,
        [decision(), decision(action="reject", suggestion_id=other_id)],
    )

    assert variant.sections[0].entries[0].bullets[0].text.startswith("Cut processing")


def test_edit_decision_requires_edited_text():
    with pytest.raises(ValidationError):
        decision(action="edit")


def test_variant_rejects_duplicate_decisions():
    with pytest.raises(ValidationError):
        schemas.ResumeVariantCreate(label="Application", decisions=[decision(), decision()])


def test_phase_two_routes_are_registered(app):
    paths = {route.path for route in app.routes}

    assert "/v1/users/{user_id}/tailoring-runs" in paths
    assert "/v1/tailoring-runs/{run_id}" in paths
    assert "/v1/tailoring-runs/{run_id}/variants" in paths
    assert "/v1/resume-variants/{variant_id}" in paths
    assert "/v1/resume-variants/{variant_id}/approve" in paths
    assert "/v1/resume-variants/{variant_id}/pdf" in paths
