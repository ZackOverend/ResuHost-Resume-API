from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.profile_records import verify_record


router = APIRouter(
    prefix="/v1/users/{user_id}/experiences",
    tags=["profile experiences"],
)


def _find_experience(db: Session, user_id: UUID, experience_id: UUID):
    experience = (
        db.query(models.Experience)
        .filter(
            models.Experience.id == experience_id,
            models.Experience.user_id == user_id,
        )
        .first()
    )
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    return experience


@router.post("", response_model=schemas.Experience, status_code=status.HTTP_201_CREATED)
def create_experience(
    user_id: UUID,
    experience: schemas.ExperienceCreate,
    db: Session = Depends(get_db),
):
    user_exists = db.query(models.User.id).filter(models.User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    next_order = (
        db.query(models.Experience)
        .filter(
            models.Experience.user_id == user_id,
            models.Experience.is_archived.is_(False),
        )
        .count()
    )
    db_experience = models.Experience(
        user_id=user_id,
        sort_order=next_order,
        **experience.model_dump(),
    )
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience


@router.post("/reorder", response_model=list[schemas.Experience])
def reorder_experiences(
    user_id: UUID,
    reorder: schemas.ProfileReorder,
    db: Session = Depends(get_db),
):
    experiences = (
        db.query(models.Experience)
        .filter(
            models.Experience.user_id == user_id,
            models.Experience.is_archived.is_(False),
        )
        .all()
    )
    by_id = {experience.id: experience for experience in experiences}
    if set(reorder.ids) != set(by_id):
        raise HTTPException(
            status_code=422,
            detail="ids must include every active experience exactly once",
        )

    for sort_order, experience_id in enumerate(reorder.ids):
        by_id[experience_id].sort_order = sort_order
    db.commit()
    return [by_id[experience_id] for experience_id in reorder.ids]


@router.patch("/{experience_id}", response_model=schemas.Experience)
def update_experience(
    user_id: UUID,
    experience_id: UUID,
    patch: schemas.ExperiencePatch,
    db: Session = Depends(get_db),
):
    experience = _find_experience(db, user_id, experience_id)
    changes = patch.model_dump(exclude_unset=True)

    editable_fields = schemas.ExperienceCreate.model_fields
    merged = {
        field: changes.get(field, getattr(experience, field))
        for field in editable_fields
    }
    validated = schemas.ExperienceCreate.model_validate(merged)
    for field, value in validated.model_dump().items():
        setattr(experience, field, value)
    if "sort_order" in changes:
        experience.sort_order = changes["sort_order"]

    db.commit()
    db.refresh(experience)
    return experience


@router.post("/{experience_id}/archive", response_model=schemas.Experience)
def archive_experience(
    user_id: UUID,
    experience_id: UUID,
    db: Session = Depends(get_db),
):
    experience = _find_experience(db, user_id, experience_id)
    if not experience.is_archived:
        experience.is_archived = True
        experience.archived_at = datetime.now(UTC)
        db.commit()
        db.refresh(experience)
    return experience


@router.post("/{experience_id}/restore", response_model=schemas.Experience)
def restore_experience(
    user_id: UUID,
    experience_id: UUID,
    db: Session = Depends(get_db),
):
    experience = _find_experience(db, user_id, experience_id)
    if experience.is_archived:
        experience.is_archived = False
        experience.archived_at = None
        experience.sort_order = (
            db.query(models.Experience)
            .filter(
                models.Experience.user_id == user_id,
                models.Experience.is_archived.is_(False),
            )
            .count()
        )
        db.commit()
        db.refresh(experience)
    return experience


@router.post("/{experience_id}/verify", response_model=schemas.Experience)
def verify_experience(
    user_id: UUID,
    experience_id: UUID,
    db: Session = Depends(get_db),
):
    experience = _find_experience(db, user_id, experience_id)
    return verify_record(db, experience)


@router.delete("/{experience_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_experience(
    user_id: UUID,
    experience_id: UUID,
    db: Session = Depends(get_db),
):
    experience = _find_experience(db, user_id, experience_id)
    if not experience.is_archived:
        raise HTTPException(
            status_code=409,
            detail="Experience must be archived before permanent deletion",
        )
    db.delete(experience)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
