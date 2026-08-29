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
    prefix="/v1/users/{user_id}/projects",
    tags=["profile projects"],
)


@router.post("", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    user_id: UUID,
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
):
    if not db.query(models.User.id).filter(models.User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    record = models.Project(
        user_id=user_id,
        sort_order=next_sort_order(db, models.Project, user_id),
        **project.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/reorder", response_model=list[schemas.Project])
def reorder_projects(
    user_id: UUID,
    reorder: schemas.ProfileReorder,
    db: Session = Depends(get_db),
):
    return reorder_records(db, models.Project, user_id, reorder.ids, "project")


@router.patch("/{project_id}", response_model=schemas.Project)
def update_project(
    user_id: UUID,
    project_id: UUID,
    patch: schemas.ProjectPatch,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Project, user_id, project_id, "Project")
    return apply_record_patch(db, record, patch, schemas.ProjectCreate)


@router.post("/{project_id}/archive", response_model=schemas.Project)
def archive_project(
    user_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Project, user_id, project_id, "Project")
    return archive_record(db, record)


@router.post("/{project_id}/restore", response_model=schemas.Project)
def restore_project(
    user_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Project, user_id, project_id, "Project")
    return restore_record(db, models.Project, user_id, record)


@router.delete("/{project_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_project(
    user_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(db, models.Project, user_id, project_id, "Project")
    permanently_delete_record(db, record, "Project")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
