from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/users/{user_id}/skill-categories", tags=["skill_categories"]
)


@router.post("/", response_model=schemas.SkillCategory)
def create_skill_category(
    user_id: int, category: schemas.SkillCategoryCreate, db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_category = models.SkillCategory(user_id=user_id, **category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/", response_model=List[schemas.SkillCategory])
def list_skill_categories(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.SkillCategory)
        .filter(models.SkillCategory.user_id == user_id)
        .all()
    )


@router.get("/{category_id}", response_model=schemas.SkillCategory)
def get_skill_category(user_id: int, category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.SkillCategory)
        .filter(
            models.SkillCategory.id == category_id,
            models.SkillCategory.user_id == user_id,
        )
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Skill category not found")
    return category


@router.put("/{category_id}", response_model=schemas.SkillCategory)
def update_skill_category(
    user_id: int,
    category_id: int,
    category: schemas.SkillCategoryCreate,
    db: Session = Depends(get_db),
):
    db_category = (
        db.query(models.SkillCategory)
        .filter(
            models.SkillCategory.id == category_id,
            models.SkillCategory.user_id == user_id,
        )
        .first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Skill category not found")
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
def delete_skill_category(
    user_id: int, category_id: int, db: Session = Depends(get_db)
):
    db_category = (
        db.query(models.SkillCategory)
        .filter(
            models.SkillCategory.id == category_id,
            models.SkillCategory.user_id == user_id,
        )
        .first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Skill category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Skill category deleted"}
