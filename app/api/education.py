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

@router.get("/{edu_id}", response_model=schemas.Education)
def get_education(user_id: int, edu_id: int, db: Session = Depends(get_db)):
    edu = db.query(models.Education).filter(models.Education.id == edu_id, models.Education.user_id == user_id).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education not found")
    return edu

@router.put("/{edu_id}", response_model=schemas.Education)
def update_education(user_id: int, edu_id: int, education: schemas.EducationCreate, db: Session = Depends(get_db)):
    db_edu = db.query(models.Education).filter(models.Education.id == edu_id, models.Education.user_id == user_id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Education not found")
    for key, value in education.model_dump().items():
        setattr(db_edu, key, value)
    db.commit()
    db.refresh(db_edu)
    return db_edu

@router.delete("/{edu_id}")
def delete_education(user_id: int, edu_id: int, db: Session = Depends(get_db)):
    db_edu = db.query(models.Education).filter(models.Education.id == edu_id, models.Education.user_id == user_id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Education not found")
    db.delete(db_edu)
    db.commit()
    return {"message": "Education deleted"}