from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session


def find_record(
    db: Session,
    model: Any,
    user_id: UUID,
    record_id: UUID,
    label: str,
):
    record = (
        db.query(model)
        .filter(model.id == record_id, model.user_id == user_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return record


def next_sort_order(db: Session, model: Any, user_id: UUID) -> int:
    return (
        db.query(model)
        .filter(model.user_id == user_id, model.is_archived.is_(False))
        .count()
    )


def reorder_records(
    db: Session,
    model: Any,
    user_id: UUID,
    ordered_ids: list[UUID],
    label: str,
):
    records = (
        db.query(model)
        .filter(model.user_id == user_id, model.is_archived.is_(False))
        .all()
    )
    by_id = {record.id: record for record in records}
    if set(ordered_ids) != set(by_id):
        raise HTTPException(
            status_code=422,
            detail=f"ids must include every active {label} exactly once",
        )
    for sort_order, record_id in enumerate(ordered_ids):
        by_id[record_id].sort_order = sort_order
    db.commit()
    return [by_id[record_id] for record_id in ordered_ids]


def apply_record_patch(
    db: Session,
    record: Any,
    patch: BaseModel,
    create_schema: type[BaseModel],
):
    changes = patch.model_dump(exclude_unset=True)
    merged = {
        field: changes.get(field, getattr(record, field))
        for field in create_schema.model_fields
    }
    validated = create_schema.model_validate(merged)
    for field, value in validated.model_dump().items():
        setattr(record, field, value)
    if "sort_order" in changes:
        record.sort_order = changes["sort_order"]
    db.commit()
    db.refresh(record)
    return record


def archive_record(db: Session, record: Any):
    if not record.is_archived:
        record.is_archived = True
        record.archived_at = datetime.now(UTC)
        db.commit()
        db.refresh(record)
    return record


def restore_record(db: Session, model: Any, user_id: UUID, record: Any):
    if record.is_archived:
        record.sort_order = next_sort_order(db, model, user_id)
        record.is_archived = False
        record.archived_at = None
        db.commit()
        db.refresh(record)
    return record


def verify_record(db: Session, record: Any):
    record.verified_at = datetime.now(UTC)
    db.commit()
    db.refresh(record)
    return record


def permanently_delete_record(db: Session, record: Any, label: str) -> None:
    if not record.is_archived:
        raise HTTPException(
            status_code=409,
            detail=f"{label} must be archived before permanent deletion",
        )
    db.delete(record)
    db.commit()
