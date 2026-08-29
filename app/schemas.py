from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing import Any, Dict, List, Optional
from typing_extensions import Annotated


NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


# ===== Experience =====
class ExperienceBase(BaseModel):
    company: NonEmptyText
    role: NonEmptyText
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ExperienceCreate(ExperienceBase):
    pass

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


# ===== Education =====
class EducationBase(BaseModel):
    institution: NonEmptyText
    degree: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: List[str] = Field(default_factory=list)

class EducationCreate(EducationBase):
    pass

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
class ProjectBase(BaseModel):
    name: NonEmptyText
    subtitle: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ProjectCreate(ProjectBase):
    pass

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
class ActivityBase(BaseModel):
    role: NonEmptyText
    organization: NonEmptyText
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)

class ActivityCreate(ActivityBase):
    pass

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


class MasterProfile(BaseModel):
    profile_version: str
    contact: ProfileContact
    education: List[Education] = Field(default_factory=list)
    experiences: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    activities: List[Activity] = Field(default_factory=list)
    skill_categories: List[SkillCategory] = Field(default_factory=list)
