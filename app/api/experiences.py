from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/experiences", tags=["experiences"])

@router.post("/", response_model=schemas.Experience)
def create_experience(user_id: int, exp: schemas.ExperienceCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_exp = models.Experience(user_id=user_id, **exp.model_dump())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.get("/", response_model=List[schemas.Experience])
def list_experiences(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Experience).filter(models.Experience.user_id == user_id).all()