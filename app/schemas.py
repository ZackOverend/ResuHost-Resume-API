from pydantic import BaseModel, EmailStr
from typing import List, Optional

# ===== Experience schemas =====
class ExperienceBase(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = []

class ExperienceCreate(ExperienceBase):
    pass

class Experience(ExperienceBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# ===== Education schemas =====
class EducationBase(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_date: Optional[str] = None

class EducationCreate(EducationBase):
    pass

class Education(EducationBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# ===== User schemas=====
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    experiences: List[Experience] = []
    education: List[Education] = []
    
    class Config:
        from_attributes = True