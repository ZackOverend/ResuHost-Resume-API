from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/education", tags=["education"])

@router.post("/", response_model=schemas.Education)
def create_education(user_id: int, education: schemas.EducationCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_education = models.Education(user_id=user_id, **education.model_dump())
    db.add(db_education)
    db.commit()
    db.refresh(db_education)
    return db_education

@router.get("/", response_model=List[schemas.Education])
def list_education(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Education).filter(models.Education.user_id == user_id).all()