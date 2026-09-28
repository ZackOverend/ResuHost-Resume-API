import re

from app import schemas
from app.resume_documents import source_hash


METRIC_PATTERN = re.compile(
    r"(?<![\w])(?:[$£€]\s*)?\d+(?:[.,]\d+)*(?:\s?(?:%|x|k|m|b|million|billion))?",
    re.IGNORECASE,
)


def _metrics(text: str) -> set[str]:
    return {match.group(0).lower().replace(" ", "") for match in METRIC_PATTERN.finditer(text)}


def verify_suggestion(
    candidate: schemas.TailoringSuggestionCandidate,
    document: schemas.ResumeDocument,
) -> schemas.TailoringSuggestion:
    issues: list[schemas.SuggestionVerificationIssue] = []
    entries_by_id = {
        entry.source_entry_id: (section.kind, entry)
        for section in document.sections
        for entry in section.entries
    }
    source = entries_by_id.get(candidate.entry_id)

    if source is None:
        issues.append(
            schemas.SuggestionVerificationIssue(
                code="missing_source_entry",
                message="The source profile entry no longer exists in this resume document.",
            )
        )
    else:
        source_section, entry = source
        if source_section != candidate.section:
            issues.append(
                schemas.SuggestionVerificationIssue(
                    code="wrong_section",
                    message="The suggestion is assigned to the wrong resume section.",
                )
            )
        bullet = next(
            (item for item in entry.bullets if item.source_index == candidate.source_index),
            None,
        )
        if bullet is None:
            issues.append(
                schemas.SuggestionVerificationIssue(
                    code="missing_source_bullet",
                    message="The referenced source bullet no longer exists.",
                )
            )
        else:
            if bullet.source_hash != candidate.source_hash:
                issues.append(
                    schemas.SuggestionVerificationIssue(
                        code="stale_source_hash",
                        message="The source bullet changed after this suggestion was created.",
                    )
                )
            if source_hash(candidate.original_text) != bullet.source_hash:
                issues.append(
                    schemas.SuggestionVerificationIssue(
                        code="source_text_changed",
                        message="The suggestion does not preserve the referenced source text.",
                    )
                )

    introduced_metrics = _metrics(candidate.proposed_text) - _metrics(
        candidate.original_text
    )
    if introduced_metrics:
        issues.append(
            schemas.SuggestionVerificationIssue(
                code="introduced_metric",
                message=(
                    "The proposed text introduces unsupported metrics: "
                    + ", ".join(sorted(introduced_metrics))
                    + "."
                ),
            )
        )

    return schemas.TailoringSuggestion(
        **candidate.model_dump(),
        verification=schemas.SuggestionVerification(
            status="fail" if issues else "pass",
            issues=issues,
        ),
    )
