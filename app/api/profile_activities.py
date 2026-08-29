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
)


router = APIRouter(
    prefix="/v1/users/{user_id}/activities",
    tags=["profile activities"],
)


@router.post("", response_model=schemas.Activity, status_code=status.HTTP_201_CREATED)
def create_activity(
    user_id: UUID,
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
):
    if not db.query(models.User.id).filter(models.User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    record = models.Activity(
        user_id=user_id,
        sort_order=next_sort_order(db, models.Activity, user_id),
        **activity.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/reorder", response_model=list[schemas.Activity])
def reorder_activities(
    user_id: UUID,
    reorder: schemas.ProfileReorder,
    db: Session = Depends(get_db),
):
    return reorder_records(db, models.Activity, user_id, reorder.ids, "activity")


@router.patch("/{activity_id}", response_model=schemas.Activity)
def update_activity(
    user_id: UUID,
    activity_id: UUID,
    patch: schemas.ActivityPatch,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Activity, user_id, activity_id, "Activity")
    return apply_record_patch(db, record, patch, schemas.ActivityCreate)


@router.post("/{activity_id}/archive", response_model=schemas.Activity)
def archive_activity(
    user_id: UUID,
    activity_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Activity, user_id, activity_id, "Activity")
    return archive_record(db, record)


@router.post("/{activity_id}/restore", response_model=schemas.Activity)
def restore_activity(
    user_id: UUID,
    activity_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Activity, user_id, activity_id, "Activity")
    return restore_record(db, models.Activity, user_id, record)


@router.delete("/{activity_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_activity(
    user_id: UUID,
    activity_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Activity, user_id, activity_id, "Activity")
    permanently_delete_record(db, record, "Activity")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
