import hashlib
from typing import Any

from app import schemas


def source_hash(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _active(records: list[Any]) -> list[Any]:
    return sorted(
        (record for record in records if not record.is_archived),
        key=lambda record: (record.sort_order, str(record.id)),
    )


def _bullets(record: Any, section: str, values: list[str] | None):
    return [
        schemas.ResumeDocumentBullet(
            text=text,
            source_section=section,
            source_entry_id=record.id,
            source_index=index,
            source_hash=source_hash(text),
        )
        for index, text in enumerate(values or [])
        if text.strip()
    ]


def build_resume_document(user: Any, profile_version: str) -> schemas.ResumeDocument:
    sections = [
        schemas.ResumeDocumentSection(
            kind="experience",
            label="Experience",
            entries=[
                schemas.ResumeDocumentEntry(
                    source_entry_id=record.id,
                    heading=record.role,
                    subheading=record.company,
                    location=record.location,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    is_current=record.is_current,
                    bullets=_bullets(record, "experience", record.bullets),
                )
                for record in _active(user.experiences)
            ],
        ),
        schemas.ResumeDocumentSection(
            kind="project",
            label="Projects",
            entries=[
                schemas.ResumeDocumentEntry(
                    source_entry_id=record.id,
                    heading=record.name,
                    subheading=record.subtitle,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    is_current=record.is_current,
                    bullets=_bullets(record, "project", record.bullets),
                )
                for record in _active(user.projects)
            ],
        ),
        schemas.ResumeDocumentSection(
            kind="education",
            label="Education",
            entries=[
                schemas.ResumeDocumentEntry(
                    source_entry_id=record.id,
                    heading=record.institution,
                    subheading=record.degree,
                    location=record.location,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    is_current=record.is_current,
                    bullets=_bullets(record, "education", record.notes),
                )
                for record in _active(user.education)
            ],
        ),
        schemas.ResumeDocumentSection(
            kind="activity",
            label="Activities",
            entries=[
                schemas.ResumeDocumentEntry(
                    source_entry_id=record.id,
                    heading=record.role,
                    subheading=record.organization,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    is_current=record.is_current,
                    bullets=_bullets(record, "activity", record.bullets),
                )
                for record in _active(user.activities)
            ],
        ),
        schemas.ResumeDocumentSection(
            kind="skill",
            label="Skills",
            entries=[
                schemas.ResumeDocumentEntry(
                    source_entry_id=record.id,
                    heading=record.name,
                    bullets=_bullets(record, "skill", record.skills),
                )
                for record in _active(user.skill_categories)
            ],
        ),
    ]
    return schemas.ResumeDocument(
        profile_version=profile_version,
        contact=schemas.ResumeDocumentContact(
            name=user.name,
            email=user.email,
            phone=user.phone,
            linkedin=user.linkedin,
            website=user.website,
        ),
        sections=[section for section in sections if section.entries],
    )
