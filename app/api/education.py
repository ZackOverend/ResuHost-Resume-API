from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/education", tags=["education"])

@router.post("/", response_model=schemas.Education)
def create_education(
    user_id: int,
    education: schemas.EducationCreate,
    db: Session = Depends(get_db)
):
    """
    Add an education record for a specific user.
    """
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create education entry
    db_education = models.Education(
        user_id=user_id,
        institution=education.institution,
        degree=education.degree,
        field=education.field,
        graduation_date=education.graduation_date
    )
    db.add(db_education)
    db.commit()
    db.refresh(db_education)
    return db_education

@router.get("/", response_model=List[schemas.Education])
def list_education(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    List all education records for a specific user.
    """
    education_list = db.query(models.Education).filter(
        models.Education.user_id == user_id
    ).all()
    return education_list