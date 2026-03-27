from fastapi import APIRouter, Depends, HTTPException
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/resume", tags=["tailor"])


def _build_resume_context(user) -> str:
    lines = []

    if user.experiences:
        lines.append("EXPERIENCES:")
        for exp in user.experiences:
            lines.append(f"  [id:{exp.id}] {exp.role} at {exp.company}")
            for bullet in exp.bullets or []:
                lines.append(f"    - {bullet}")

    if user.projects:
        lines.append("PROJECTS:")
        for proj in user.projects:
            lines.append(f"  [id:{proj.id}] {proj.name}")
            for bullet in proj.bullets or []:
                lines.append(f"    - {bullet}")

    if user.activities:
        lines.append("ACTIVITIES:")
        for act in user.activities:
            lines.append(f"  [id:{act.id}] {act.role} at {act.organization}")
            for bullet in act.bullets or []:
                lines.append(f"    - {bullet}")

    return "\n".join(lines)


@router.post("/{user_id}/tailor", response_model=schemas.TailorResponse)
async def tailor_resume(
    user_id: int, request: schemas.TailorRequest, db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    resume_context = _build_resume_context(user)
    if not resume_context:
        raise HTTPException(
            status_code=400,
            detail="User has no experiences, projects, or activities to tailor",
        )

    provider = OpenAIProvider(base_url=f"{request.host}/v1", api_key=request.api_key)
    agent = Agent(
        OpenAIChatModel(request.model, provider=provider),
        output_type=schemas.TailorResponse,
        system_prompt=(
            "You are a professional resume writer. "
            "Given a job description and a set of resume bullet points, rewrite the bullets "
            "to be more relevant and impactful for the role. "
            "Use strong action verbs, be concise, and highlight transferable skills. "
            "Return the same number of bullets per section and preserve the original IDs. "
            "Only return the structured data — no explanation or commentary."
        ),
    )

    prompt = (
        f"Job Description:\n{request.job_description}\n\n"
        f"Resume Content:\n{resume_context}\n\n"
        "Tailor the bullet points for each section to match the job description. "
        "Include all sections and preserve their IDs."
    )

    try:
        result = await agent.run(prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {str(e)}")

    return result.output


@router.patch("/{user_id}/apply-tailor", response_model=schemas.User)
def apply_tailor(
    user_id: int, tailor: schemas.TailorResponse, db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for item in tailor.experiences:
        exp = (
            db.query(models.Experience)
            .filter(
                models.Experience.id == item.id, models.Experience.user_id == user_id
            )
            .first()
        )
        if exp:
            setattr(exp, "bullets", item.bullets)

    for item in tailor.projects:
        proj = (
            db.query(models.Project)
            .filter(models.Project.id == item.id, models.Project.user_id == user_id)
            .first()
        )
        if proj:
            setattr(proj, "bullets", item.bullets)

    for item in tailor.activities:
        act = (
            db.query(models.Activity)
            .filter(models.Activity.id == item.id, models.Activity.user_id == user_id)
            .first()
        )
        if act:
            setattr(act, "bullets", item.bullets)

    db.commit()
    db.refresh(user)
    return user
