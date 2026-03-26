from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional


# ===== Experience =====
class ExperienceBase(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = []

class ExperienceCreate(ExperienceBase):
    pass

class Experience(ExperienceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ===== Education =====
class EducationBase(BaseModel):
    institution: str
    degree: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: List[str] = []

class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ===== Project =====
class ProjectBase(BaseModel):
    name: str
    subtitle: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = []

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ===== Activity =====
class ActivityBase(BaseModel):
    role: str
    organization: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = []

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ===== SkillCategory =====
class SkillCategoryBase(BaseModel):
    name: str
    skills: List[str] = []

class SkillCategoryCreate(SkillCategoryBase):
    pass

class SkillCategory(SkillCategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ===== Resume Snapshot =====
class ResumeSnapshotCreate(BaseModel):
    label: str

class ResumeSnapshot(BaseModel):
    id: int
    user_id: int
    label: str
    created_at: datetime
    data: Dict[str, Any]

    class Config:
        from_attributes = True


# ===== Tailor =====
class TailorRequest(BaseModel):
    job_description: str
    model: str = "qwen3.5:cloud"
    host: str = "http://localhost:11434"

class TailoredExperience(BaseModel):
    id: int
    bullets: List[str]

class TailoredProject(BaseModel):
    id: int
    bullets: List[str]

class TailoredActivity(BaseModel):
    id: int
    bullets: List[str]

class TailorResponse(BaseModel):
    experiences: List[TailoredExperience]
    projects: List[TailoredProject]
    activities: List[TailoredActivity]


# ===== User =====
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    education: List[Education] = []
    experiences: List[Experience] = []
    projects: List[Project] = []
    activities: List[Activity] = []
    skill_categories: List[SkillCategory] = []

    class Config:
        from_attributes = True
