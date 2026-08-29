from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.profile_records import (
    apply_record_patch,
    archive_record,
    find_record,
    next_sort_order,
    permanently_delete_record,
    reorder_records,
    restore_record,
    verify_record,
)


router = APIRouter(
    prefix="/v1/users/{user_id}/education",
    tags=["profile education"],
)


@router.post("", response_model=schemas.Education, status_code=status.HTTP_201_CREATED)
def create_education(
    user_id: UUID,
    education: schemas.EducationCreate,
    db: Session = Depends(get_db),
):
    if not db.query(models.User.id).filter(models.User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    record = models.Education(
        user_id=user_id,
        sort_order=next_sort_order(db, models.Education, user_id),
        **education.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/reorder", response_model=list[schemas.Education])
def reorder_education(
    user_id: UUID,
    reorder: schemas.ProfileReorder,
    db: Session = Depends(get_db),
):
    return reorder_records(db, models.Education, user_id, reorder.ids, "education record")


@router.patch("/{education_id}", response_model=schemas.Education)
def update_education(
    user_id: UUID,
    education_id: UUID,
    patch: schemas.EducationPatch,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Education, user_id, education_id, "Education")
    return apply_record_patch(db, record, patch, schemas.EducationCreate)


@router.post("/{education_id}/archive", response_model=schemas.Education)
def archive_education(
    user_id: UUID,
    education_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Education, user_id, education_id, "Education")
    return archive_record(db, record)


@router.post("/{education_id}/restore", response_model=schemas.Education)
def restore_education(
    user_id: UUID,
    education_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Education, user_id, education_id, "Education")
    return restore_record(db, models.Education, user_id, record)


@router.post("/{education_id}/verify", response_model=schemas.Education)
def verify_education(user_id: UUID, education_id: UUID, db: Session = Depends(get_db)):
    record = find_record(db, models.Education, user_id, education_id, "Education")
    return verify_record(db, record)


@router.delete("/{education_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_education(
    user_id: UUID,
    education_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Education, user_id, education_id, "Education")
    permanently_delete_record(db, record, "Education")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
