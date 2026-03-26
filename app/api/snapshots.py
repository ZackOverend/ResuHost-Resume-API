from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.api.resume import build_user_data
from app.database import get_db

router = APIRouter(prefix="/users/{user_id}/resumes", tags=["snapshots"])


@router.post("/", response_model=schemas.ResumeSnapshot)
def create_snapshot(user_id: int, body: schemas.ResumeSnapshotCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    snapshot = models.Resume(user_id=user_id, label=body.label, data=build_user_data(user))
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


@router.get("/", response_model=List[schemas.ResumeSnapshot])
def list_snapshots(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Resume).filter(models.Resume.user_id == user_id).all()


@router.get("/{resume_id}", response_model=schemas.ResumeSnapshot)
def get_snapshot(user_id: int, resume_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == user_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.delete("/{resume_id}")
def delete_snapshot(user_id: int, resume_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == user_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    db.delete(snapshot)
    db.commit()
    return {"message": "Snapshot deleted"}
