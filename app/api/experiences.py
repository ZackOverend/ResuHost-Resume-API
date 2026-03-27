from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/experiences", tags=["experiences"])

@router.post("/", response_model=schemas.Experience)
def create_experience(user_id: UUID, exp: schemas.ExperienceCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_exp = models.Experience(user_id=user_id, **exp.model_dump())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.get("/", response_model=List[schemas.Experience])
def list_experiences(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Experience).filter(models.Experience.user_id == user_id).all()

@router.get("/{exp_id}", response_model=schemas.Experience)
def get_experience(user_id: UUID, exp_id: UUID, db: Session = Depends(get_db)):
    exp = db.query(models.Experience).filter(models.Experience.id == exp_id, models.Experience.user_id == user_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp

@router.put("/{exp_id}", response_model=schemas.Experience)
def update_experience(user_id: UUID, exp_id: UUID, exp: schemas.ExperienceCreate, db: Session = Depends(get_db)):
    db_exp = db.query(models.Experience).filter(models.Experience.id == exp_id, models.Experience.user_id == user_id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    for key, value in exp.model_dump().items():
        setattr(db_exp, key, value)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.delete("/{exp_id}")
def delete_experience(user_id: UUID, exp_id: UUID, db: Session = Depends(get_db)):
    db_exp = db.query(models.Experience).filter(models.Experience.id == exp_id, models.Experience.user_id == user_id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(db_exp)
    db.commit()
    return {"message": "Experience deleted"}
