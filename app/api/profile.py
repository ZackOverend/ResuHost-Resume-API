import hashlib
import json
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
