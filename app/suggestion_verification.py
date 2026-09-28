import re

from app import schemas
from app.resume_documents import source_hash


METRIC_PATTERN = re.compile(
    r"(?<![\w])(?:[$£€]\s*)?\d+(?:[.,]\d+)*(?:\s?(?:%|x|k|m|b|million|billion))?",
    re.IGNORECASE,
)

TERM_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+#]*(?:[.\-/][A-Za-z0-9+#]+)*")
CREDENTIAL_PATTERN = re.compile(
    r"\b(?:certified|certification|certificate|licensed|accredited|patent(?:ed)?|"
    r"award(?:ed)?|ph\.?d|mba)\b",
    re.IGNORECASE,
)


def _metrics(text: str) -> set[str]:
    return {match.group(0).lower().replace(" ", "") for match in METRIC_PATTERN.finditer(text)}


def _starts_sentence(text: str, position: int) -> bool:
    preceding = text[:position].rstrip()
    return not preceding or preceding.endswith((".", "!", "?", ":", ";"))


def _named_terms(text: str) -> set[str]:
    """Proper nouns, acronyms, and technology names, skipping sentence-initial words."""
    terms = set()
    for match in TERM_PATTERN.finditer(text):
        term = match.group(0)
        if len(term) < 2:
            continue
        distinctive = any(char.isupper() for char in term[1:]) or any(
            char.isdigit() or char in "+#" for char in term
        )
        if distinctive or (term[0].isupper() and not _starts_sentence(text, match.start())):
            terms.add(term)
    return terms


def _words(text: str) -> set[str]:
    return {match.group(0).lower() for match in TERM_PATTERN.finditer(text)}


def _credentials(text: str) -> set[str]:
    return {match.group(0).lower() for match in CREDENTIAL_PATTERN.finditer(text)}


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

    evidence = candidate.original_text
    if source is not None:
        entry = source[1]
        evidence = " ".join(
            filter(None, [candidate.original_text, entry.heading, entry.subheading, entry.location])
        )
    evidence_words = _words(evidence)

    introduced_terms = sorted(
        term for term in _named_terms(candidate.proposed_text) if term.lower() not in evidence_words
    )
    if introduced_terms:
        issues.append(
            schemas.SuggestionVerificationIssue(
                code="introduced_named_term",
                message=(
                    "The proposed text introduces names or terms not found in the source entry: "
                    + ", ".join(introduced_terms)
                    + "."
                ),
            )
        )

    introduced_credentials = _credentials(candidate.proposed_text) - _credentials(evidence)
    if introduced_credentials:
        issues.append(
            schemas.SuggestionVerificationIssue(
                code="introduced_credential",
                message=(
                    "The proposed text introduces unsupported credential language: "
                    + ", ".join(sorted(introduced_credentials))
                    + "."
                ),
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
