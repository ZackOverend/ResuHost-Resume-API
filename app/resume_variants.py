from fastapi import HTTPException

from app import schemas
from app.suggestion_verification import verify_suggestion


def create_variant_document(
    source: schemas.ResumeDocument,
    suggestions: list[schemas.TailoringSuggestion],
    decisions: list[schemas.VariantSuggestionDecision],
) -> schemas.ResumeDocument:
    suggestions_by_id = {suggestion.id: suggestion for suggestion in suggestions}
    document = source.model_copy(deep=True)
    bullets = {
        (bullet.source_section, bullet.source_entry_id, bullet.source_index): bullet
        for section in document.sections
        for entry in section.entries
        for bullet in entry.bullets
    }
    changed: set[tuple] = set()

    for decision in decisions:
        suggestion = suggestions_by_id.get(decision.suggestion_id)
        if suggestion is None:
            raise HTTPException(status_code=422, detail="Decision references an unknown suggestion")
        if decision.action == "reject":
            continue

        candidate = schemas.TailoringSuggestionCandidate(
            **suggestion.model_dump(exclude={"verification", "proposed_text"}),
            proposed_text=decision.edited_text or suggestion.proposed_text,
        )
        verified = verify_suggestion(candidate, source)
        if verified.verification.status != "pass":
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "A selected suggestion failed verification: "
                    + " ".join(issue.message for issue in verified.verification.issues),
                    "suggestion_id": str(suggestion.id),
                    "issues": [issue.model_dump() for issue in verified.verification.issues],
                },
            )
        key = (suggestion.section, suggestion.entry_id, suggestion.source_index)
        if key in changed:
            raise HTTPException(
                status_code=422,
                detail="Only one suggestion may be selected for each source bullet",
            )
        changed.add(key)
        bullet = bullets.get(key)
        if bullet is None:
            raise HTTPException(status_code=422, detail="Suggestion source is not in the resume document")
        bullet.text = candidate.proposed_text

    return document
