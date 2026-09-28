from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app import models, schemas
from app.api.profile import get_profile
from app.api.resume import render_pdf
from app.config import Settings, get_request_settings
from app.database import get_db
from app.resume_documents import build_resume_document
from app.resume_variants import create_variant_document
from app.tailoring import build_tailoring_agent, resolve_proposals, tailoring_prompt


router = APIRouter(prefix="/v1", tags=["tailoring"])


def _variant_pdf_data(document: schemas.ResumeDocument) -> dict:
    by_kind = {section.kind: section for section in document.sections}

    def entries(kind: str) -> list[schemas.ResumeDocumentEntry]:
        section = by_kind.get(kind)
        return section.entries if section else []

    def dates(entry: schemas.ResumeDocumentEntry) -> dict:
        return {
            "start_date": entry.start_date or "",
            "end_date": "Present" if entry.is_current else entry.end_date or "",
        }

    return {
        **document.contact.model_dump(),
        "phone": document.contact.phone or "",
        "linkedin": document.contact.linkedin or "",
        "website": document.contact.website or "",
        "experiences": [
            {
                "role": entry.heading,
                "company": entry.subheading or "",
                "location": entry.location or "",
                "bullets": [bullet.text for bullet in entry.bullets],
                **dates(entry),
            }
            for entry in entries("experience")
        ],
        "projects": [
            {
                "name": entry.heading,
                "subtitle": entry.subheading or "",
                "bullets": [bullet.text for bullet in entry.bullets],
                **dates(entry),
            }
            for entry in entries("project")
        ],
        "education": [
            {
                "institution": entry.heading,
                "degree": entry.subheading or "",
                "location": entry.location or "",
                "notes": [bullet.text for bullet in entry.bullets],
                **dates(entry),
            }
            for entry in entries("education")
        ],
        "activities": [
            {
                "role": entry.heading,
                "organization": entry.subheading or "",
                "bullets": [bullet.text for bullet in entry.bullets],
                **dates(entry),
            }
            for entry in entries("activity")
        ],
        "skill_categories": [
            {
                "name": entry.heading,
                "skills": [bullet.text for bullet in entry.bullets],
            }
            for entry in entries("skill")
        ],
    }


@router.post(
    "/users/{user_id}/tailoring-runs",
    response_model=schemas.TailoringRunResponse,
    status_code=201,
)
async def create_tailoring_run(
    user_id: UUID,
    request: schemas.TailoringRunCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_request_settings),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    model_name = request.model or settings.ollama_model
    if model_name not in settings.allowed_models:
        raise HTTPException(status_code=400, detail="Requested model is not allowed")

    profile = get_profile(user_id, db)
    document = build_resume_document(user, profile["profile_version"])
    if not any(entry.bullets for section in document.sections for entry in section.entries):
        raise HTTPException(status_code=400, detail="Profile has no resume bullets to tailor")

    run = models.TailoringRun(
        user_id=user_id,
        profile_version=document.profile_version,
        job_description=request.job_description,
        model=model_name,
        status="pending",
        suggestions=[],
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    agent = build_tailoring_agent(settings, model_name)
    try:
        result = await agent.run(tailoring_prompt(request.job_description, document))
        run.suggestions = [
            suggestion.model_dump(mode="json")
            for suggestion in resolve_proposals(result.output.suggestions, document)
        ]
        run.status = "completed"
        run.completed_at = datetime.now(UTC)
        db.commit()
        db.refresh(run)
    except Exception:
        run.status = "failed"
        run.error_message = "The model provider could not complete the tailoring run"
        run.completed_at = datetime.now(UTC)
        db.commit()
        raise HTTPException(status_code=502, detail=run.error_message)

    return run


@router.get("/tailoring-runs/{run_id}", response_model=schemas.TailoringRunResponse)
def get_tailoring_run(run_id: UUID, db: Session = Depends(get_db)):
    run = db.query(models.TailoringRun).filter(models.TailoringRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Tailoring run not found")
    return run


@router.post(
    "/tailoring-runs/{run_id}/variants",
    response_model=schemas.ResumeVariantResponse,
    status_code=201,
)
def create_resume_variant(
    run_id: UUID,
    request: schemas.ResumeVariantCreate,
    db: Session = Depends(get_db),
):
    run = db.query(models.TailoringRun).filter(models.TailoringRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Tailoring run not found")
    if run.status != "completed":
        raise HTTPException(status_code=409, detail="Tailoring run is not complete")

    user = db.query(models.User).filter(models.User.id == run.user_id).first()
    profile = get_profile(run.user_id, db)
    if profile["profile_version"] != run.profile_version:
        raise HTTPException(status_code=409, detail="The source profile changed after this tailoring run")

    source = build_resume_document(user, run.profile_version)
    suggestions = [schemas.TailoringSuggestion.model_validate(item) for item in run.suggestions]
    document = create_variant_document(source, suggestions, request.decisions)
    variant = models.ResumeVariant(
        user_id=run.user_id,
        tailoring_run_id=run.id,
        label=request.label,
        profile_version=run.profile_version,
        status="draft",
        document=document.model_dump(mode="json"),
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


@router.get("/resume-variants/{variant_id}", response_model=schemas.ResumeVariantResponse)
def get_resume_variant(variant_id: UUID, db: Session = Depends(get_db)):
    variant = db.query(models.ResumeVariant).filter(models.ResumeVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Resume variant not found")
    return variant


@router.post("/resume-variants/{variant_id}/approve", response_model=schemas.ResumeVariantResponse)
def approve_resume_variant(variant_id: UUID, db: Session = Depends(get_db)):
    variant = db.query(models.ResumeVariant).filter(models.ResumeVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Resume variant not found")
    if variant.status != "approved":
        variant.status = "approved"
        variant.approved_at = datetime.now(UTC)
        db.commit()
        db.refresh(variant)
    return variant


@router.get("/resume-variants/{variant_id}/pdf", response_class=Response)
def get_resume_variant_pdf(variant_id: UUID, db: Session = Depends(get_db)):
    variant = db.query(models.ResumeVariant).filter(models.ResumeVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Resume variant not found")
    document = schemas.ResumeDocument.model_validate(variant.document)
    return render_pdf(_variant_pdf_data(document), f"resume-{variant.id}.pdf")
