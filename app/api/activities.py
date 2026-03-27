from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/activities", tags=["activities"])

@router.post("/", response_model=schemas.Activity)
def create_activity(user_id: UUID, activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_activity = models.Activity(user_id=user_id, **activity.model_dump())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.get("/", response_model=List[schemas.Activity])
def list_activities(user_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Activity).filter(models.Activity.user_id == user_id).all()

@router.get("/{activity_id}", response_model=schemas.Activity)
def get_activity(user_id: UUID, activity_id: UUID, db: Session = Depends(get_db)):
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.user_id == user_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.put("/{activity_id}", response_model=schemas.Activity)
def update_activity(user_id: UUID, activity_id: UUID, activity: schemas.ActivityCreate, db: Session = Depends(get_db)):
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.user_id == user_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    for key, value in activity.model_dump().items():
        setattr(db_activity, key, value)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete("/{activity_id}")
def delete_activity(user_id: UUID, activity_id: UUID, db: Session = Depends(get_db)):
    db_activity = db.query(models.Activity).filter(models.Activity.id == activity_id, models.Activity.user_id == user_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(db_activity)
    db.commit()
    return {"message": "Activity deleted"}
