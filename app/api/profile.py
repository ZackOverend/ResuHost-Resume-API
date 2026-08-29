import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db


router = APIRouter(prefix="/v1/users/{user_id}/profile", tags=["profile"])


def _ordered(records: list[Any]) -> list[Any]:
    return sorted(
        records,
        key=lambda record: (record.is_archived, record.sort_order, str(record.id)),
    )


def _profile_version(profile_data: dict[str, Any]) -> str:
    payload = json.dumps(
        profile_data,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@router.get("", response_model=schemas.MasterProfile)
def get_profile(user_id: UUID, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .options(
            selectinload(models.User.education),
            selectinload(models.User.experiences),
            selectinload(models.User.projects),
            selectinload(models.User.activities),
            selectinload(models.User.skill_categories),
        )
        .filter(models.User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile_data = {
        "contact": schemas.ProfileContact.model_validate(user).model_dump(mode="json"),
        "education": [
            schemas.Education.model_validate(item).model_dump(mode="json")
            for item in _ordered(user.education)
        ],
        "experiences": [
            schemas.Experience.model_validate(item).model_dump(mode="json")
            for item in _ordered(user.experiences)
        ],
        "projects": [
            schemas.Project.model_validate(item).model_dump(mode="json")
            for item in _ordered(user.projects)
        ],
        "activities": [
            schemas.Activity.model_validate(item).model_dump(mode="json")
            for item in _ordered(user.activities)
        ],
        "skill_categories": [
            schemas.SkillCategory.model_validate(item).model_dump(mode="json")
            for item in _ordered(user.skill_categories)
        ],
    }
    return {"profile_version": _profile_version(profile_data), **profile_data}


@router.patch("", response_model=schemas.MasterProfile)
def update_profile(
    user_id: UUID,
    patch: schemas.ProfileContactPatch,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    changes = patch.model_dump(exclude_unset=True)
    for required_field in ("name", "email"):
        if required_field in changes and changes[required_field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{required_field.capitalize()} cannot be null",
            )

    if "email" in changes:
        email_owner = (
            db.query(models.User)
            .filter(
                models.User.email == changes["email"],
                models.User.id != user_id,
            )
            .first()
        )
        if email_owner:
            raise HTTPException(status_code=409, detail="Email already registered")

    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()

    return get_profile(user_id, db)


@router.post("/verify", response_model=schemas.MasterProfile)
def verify_profile_contact(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.verified_at = datetime.now(UTC)
    db.commit()
    return get_profile(user_id, db)
