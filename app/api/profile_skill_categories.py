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
    prefix="/v1/users/{user_id}/skill-categories",
    tags=["profile skill categories"],
)


@router.post(
    "",
    response_model=schemas.SkillCategory,
    status_code=status.HTTP_201_CREATED,
)
def create_skill_category(
    user_id: UUID,
    category: schemas.SkillCategoryCreate,
    db: Session = Depends(get_db),
):
    if not db.query(models.User.id).filter(models.User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    record = models.SkillCategory(
        user_id=user_id,
        sort_order=next_sort_order(db, models.SkillCategory, user_id),
        **category.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/reorder", response_model=list[schemas.SkillCategory])
def reorder_skill_categories(
    user_id: UUID,
    reorder: schemas.ProfileReorder,
    db: Session = Depends(get_db),
):
    return reorder_records(
        db,
        models.SkillCategory,
        user_id,
        reorder.ids,
        "skill category",
    )


@router.patch("/{category_id}", response_model=schemas.SkillCategory)
def update_skill_category(
    user_id: UUID,
    category_id: UUID,
    patch: schemas.SkillCategoryPatch,
    db: Session = Depends(get_db),
):
    record = find_record(
        db,
        models.SkillCategory,
        user_id,
        category_id,
        "Skill category",
    )
    return apply_record_patch(db, record, patch, schemas.SkillCategoryCreate)


@router.post("/{category_id}/archive", response_model=schemas.SkillCategory)
def archive_skill_category(
    user_id: UUID,
    category_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(
        db,
        models.SkillCategory,
        user_id,
        category_id,
        "Skill category",
    )
    return archive_record(db, record)


@router.post("/{category_id}/restore", response_model=schemas.SkillCategory)
def restore_skill_category(
    user_id: UUID,
    category_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(
        db,
        models.SkillCategory,
        user_id,
        category_id,
        "Skill category",
    )
    return restore_record(db, models.SkillCategory, user_id, record)


@router.delete("/{category_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_skill_category(
    user_id: UUID,
    category_id: UUID,
    db: Session = Depends(get_db),
):
    record = find_record(
        db,
        models.SkillCategory,
        user_id,
        category_id,
        "Skill category",
    )
    permanently_delete_record(db, record, "Skill category")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
