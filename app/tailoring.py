from uuid import uuid4

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app import schemas
from app.config import Settings
from app.suggestion_verification import verify_suggestion


SYSTEM_PROMPT = (
    "Propose truthful resume bullet edits grounded only in the supplied resume. "
    "Each suggestion must reference exactly one bullet by its label, such as b3. "
    "Do not introduce facts, metrics, technologies, credentials, employers, titles, "
    "or dates that are not in the resume. Omit bullets that need no change."
)


def bullet_refs(document: schemas.ResumeDocument) -> dict[str, schemas.ResumeDocumentBullet]:
    bullets = (
        bullet
        for section in document.sections
        for entry in section.entries
        for bullet in entry.bullets
    )
    return {f"b{number}": bullet for number, bullet in enumerate(bullets, start=1)}


def _entry_label(entry: schemas.ResumeDocumentEntry) -> str:
    label = entry.heading
    if entry.subheading:
        label += f" — {entry.subheading}"
    end = "Present" if entry.is_current else entry.end_date
    if entry.start_date or end:
        label += f" ({entry.start_date or '?'} – {end or '?'})"
    return label


def tailoring_prompt(job_description: str, document: schemas.ResumeDocument) -> str:
    refs = {id(bullet): ref for ref, bullet in bullet_refs(document).items()}
    lines = [f"Job description:\n{job_description}", "", "Resume:"]
    for section in document.sections:
        lines.append(f"\n## {section.label}")
        for entry in section.entries:
            lines.append(_entry_label(entry))
            lines.extend(f"  {refs[id(bullet)]}: {bullet.text}" for bullet in entry.bullets)
    return "\n".join(lines)


def resolve_proposals(
    proposals: list[schemas.TailoringProposal],
    document: schemas.ResumeDocument,
) -> list[schemas.TailoringSuggestion]:
    refs = bullet_refs(document)
    suggestions = []
    for proposal in proposals:
        bullet = refs.get(proposal.bullet_ref.strip().lower())
        if bullet is None or proposal.proposed_text == bullet.text:
            continue
        candidate = schemas.TailoringSuggestionCandidate(
            id=uuid4(),
            section=bullet.source_section,
            entry_id=bullet.source_entry_id,
            source_index=bullet.source_index,
            source_hash=bullet.source_hash,
            original_text=bullet.text,
            proposed_text=proposal.proposed_text,
            reason=proposal.reason,
            matched_requirements=proposal.matched_requirements,
        )
        suggestions.append(verify_suggestion(candidate, document))
    return suggestions


def build_tailoring_agent(settings: Settings, model_name: str) -> Agent:
    provider = OpenAIProvider(base_url=f"{settings.ollama_host}/v1", api_key=settings.ollama_api_key)
    return Agent(
        OpenAIChatModel(model_name, provider=provider),
        output_type=schemas.TailoringProposals,
        system_prompt=SYSTEM_PROMPT,
    )
