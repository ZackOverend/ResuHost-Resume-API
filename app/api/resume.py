from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from jinja2 import Template
from weasyprint import HTML
from typing import Any, Dict, Optional, cast
from uuid import UUID
import os

from app import models
from app.database import get_db

router = APIRouter(prefix="/resume", tags=["resume"])

# Load HTML template once at startup
template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "resume_template_dynamic.html")
with open(template_path, "r") as f:
    HTML_TEMPLATE = f.read()


def build_user_data(user) -> dict:
    return {
        "name": user.name,
        "email": user.email,
        "phone": user.phone or "",
        "linkedin": user.linkedin or "",
        "website": user.website or "",
        "experiences": [
            {
                "company": exp.company,
                "role": exp.role,
                "location": exp.location or "",
                "start_date": exp.start_date or "",
                "end_date": exp.end_date or "",
                "bullets": exp.bullets or []
            }
            for exp in user.experiences
        ],
        "education": [
            {
                "institution": edu.institution,
                "degree": edu.degree or "",
                "location": edu.location or "",
                "start_date": edu.start_date or "",
                "end_date": edu.end_date or "",
                "notes": edu.notes or []
            }
            for edu in user.education
        ],
        "projects": [
            {
                "name": proj.name,
                "subtitle": proj.subtitle or "",
                "start_date": proj.start_date or "",
                "end_date": proj.end_date or "",
                "bullets": proj.bullets or []
            }
            for proj in user.projects
        ],
        "activities": [
            {
                "role": act.role,
                "organization": act.organization,
                "start_date": act.start_date or "",
                "end_date": act.end_date or "",
                "bullets": act.bullets or []
            }
            for act in user.activities
        ],
        "skill_categories": [
            {
                "name": sc.name,
                "skills": sc.skills or []
            }
            for sc in user.skill_categories
        ],
    }


def render_pdf(user_data: dict, filename: str) -> Response:
    try:
        html_out = Template(HTML_TEMPLATE).render(**user_data)
        pdf = HTML(string=html_out).write_pdf()
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/{user_id}", response_class=Response)
def generate_resume(user_id: int, snapshot_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if snapshot_id is not None:
        snapshot = db.query(models.Resume).filter(
            models.Resume.id == snapshot_id,
            models.Resume.user_id == user_id
        ).first()
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        user_data = cast(Dict[str, Any], snapshot.data)
    else:
        user_data = build_user_data(user)

    return render_pdf(user_data, f"{user.name}_resume.pdf")