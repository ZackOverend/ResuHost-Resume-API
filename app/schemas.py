from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, model_validator
from typing import Any, Dict, List, Optional
from typing_extensions import Annotated


NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
MonthText = Annotated[str, StringConstraints(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]


class DateRange(BaseModel):
    start_date: Optional[MonthText] = None
    end_date: Optional[MonthText] = None
    is_current: bool = False

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.is_current and self.end_date is not None:
            raise ValueError("end_date must be omitted when is_current is true")
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be earlier than start_date")
        return self


# ===== Experience =====
class ExperienceBase(DateRange):
    company: NonEmptyText
    role: NonEmptyText
    location: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ExperienceCreate(ExperienceBase):
    pass


class ExperiencePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: Optional[NonEmptyText] = None
    role: Optional[NonEmptyText] = None
    location: Optional[str] = None
    start_date: Optional[MonthText] = None
    end_date: Optional[MonthText] = None
    is_current: Optional[bool] = None
    bullets: Optional[List[str]] = None
    sort_order: Optional[int] = Field(default=None, ge=0)


class Experience(ExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    sort_order: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


class ProfileReorder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ids: List[UUID]

    @model_validator(mode="after")
    def validate_unique_ids(self):
        if len(self.ids) != len(set(self.ids)):
            raise ValueError("ids must not contain duplicates")
        return self


# ===== Education =====
class EducationBase(DateRange):
    institution: NonEmptyText
    degree: Optional[str] = None
    location: Optional[str] = None
    notes: List[str] = Field(default_factory=list)

class EducationCreate(EducationBase):
    pass


class EducationPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: Optional[NonEmptyText] = None
    degree: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[MonthText] = None
    end_date: Optional[MonthText] = None
    is_current: Optional[bool] = None
    notes: Optional[List[str]] = None
    sort_order: Optional[int] = Field(default=None, ge=0)


class Education(EducationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    sort_order: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# ===== Project =====
class ProjectBase(DateRange):
    name: NonEmptyText
    subtitle: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ProjectCreate(ProjectBase):
    pass


class ProjectPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[NonEmptyText] = None
    subtitle: Optional[str] = None
    start_date: Optional[MonthText] = None
    end_date: Optional[MonthText] = None
    is_current: Optional[bool] = None
    bullets: Optional[List[str]] = None
    sort_order: Optional[int] = Field(default=None, ge=0)


class Project(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    sort_order: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# ===== Activity =====
class ActivityBase(DateRange):
    role: NonEmptyText
    organization: NonEmptyText
    bullets: List[str] = Field(default_factory=list)

class ActivityCreate(ActivityBase):
    pass


class ActivityPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Optional[NonEmptyText] = None
    organization: Optional[NonEmptyText] = None
    start_date: Optional[MonthText] = None
    end_date: Optional[MonthText] = None
    is_current: Optional[bool] = None
    bullets: Optional[List[str]] = None
    sort_order: Optional[int] = Field(default=None, ge=0)


class Activity(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    sort_order: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# ===== SkillCategory =====
class SkillCategoryBase(BaseModel):
    name: NonEmptyText
    skills: List[str] = Field(default_factory=list)

class SkillCategoryCreate(SkillCategoryBase):
    pass


class SkillCategoryPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[NonEmptyText] = None
    skills: Optional[List[str]] = None
    sort_order: Optional[int] = Field(default=None, ge=0)


class SkillCategory(SkillCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    sort_order: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


# ===== Resume Snapshot =====
class ResumeSnapshotCreate(BaseModel):
    label: NonEmptyText

class ResumeSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    label: str
    created_at: datetime
    data: Dict[str, Any]

# ===== Tailor =====
class TailorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_description: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=50, max_length=50_000),
    ]
    model: Optional[str] = None

class TailoredExperience(BaseModel):
    id: UUID
    bullets: List[str] = Field(default_factory=list)

class TailoredProject(BaseModel):
    id: UUID
    bullets: List[str] = Field(default_factory=list)

class TailoredActivity(BaseModel):
    id: UUID
    bullets: List[str] = Field(default_factory=list)

class TailorResponse(BaseModel):
    experiences: List[TailoredExperience] = Field(default_factory=list)
    projects: List[TailoredProject] = Field(default_factory=list)
    activities: List[TailoredActivity] = Field(default_factory=list)


# ===== User =====
class UserBase(BaseModel):
    name: NonEmptyText
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None
    education: List[Education] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    activities: List[Activity] = Field(default_factory=list)
    skill_categories: List[SkillCategory] = Field(default_factory=list)


class ProfileContact(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None


class ProfileContactPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[NonEmptyText] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None


class MasterProfile(BaseModel):
    profile_version: str
    contact: ProfileContact
    education: List[Education] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    activities: List[Activity] = Field(default_factory=list)
    skill_categories: List[SkillCategory] = Field(default_factory=list)
