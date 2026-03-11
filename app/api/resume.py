from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from jinja2 import Template
from weasyprint import HTML
import os

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/resume", tags=["resume"])

# Load HTML template once at startup
template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "resume_template.html")
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
        "summary": user.summary or "",
        "skills": user.skills or [],
        "experiences": [
            {
                "company": exp.company,
                "role": exp.role,
                "start_date": exp.start_date or "",
                "end_date": exp.end_date or "",
                "description": exp.description or []
            }
            for exp in user.experiences
        ],
        "education": [
            {
                "institution": edu.institution,
                "degree": edu.degree or "",
                "field": edu.field or "",
                "graduation_date": edu.graduation_date or ""
            }
            for edu in user.education
        ]
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