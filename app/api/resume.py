from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from jinja2 import Template
from weasyprint import HTML
import os

from app import models
from app.database import get_db

router = APIRouter(prefix="/resume", tags=["resume"])

# Load HTML template once at startup
template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "resume_template_dynamic.html")
with open(template_path, "r") as f:
    HTML_TEMPLATE = f.read()

@router.post("/{user_id}", response_class=Response)
def generate_resume(user_id: int, db: Session = Depends(get_db)):
    """
    Generate a PDF resume for the given user.
    """
    # Fetch user with experiences and education
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prepare data for template
    user_data = {
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

    try:
        # Render HTML
        template = Template(HTML_TEMPLATE)
        html_out = template.render(**user_data)

        # Generate PDF
        pdf = HTML(string=html_out).write_pdf()

        # Return PDF
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={user.name}_resume.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")