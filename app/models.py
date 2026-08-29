import uuid

from sqlalchemy import ARRAY, JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    linkedin = Column(String)
    website = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    verified_at = Column(DateTime(timezone=True))

    education = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )
    experiences = relationship(
        "Experience", back_populates="user", cascade="all, delete-orphan"
    )
    projects = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    activities = relationship(
        "Activity", back_populates="user", cascade="all, delete-orphan"
    )
    skill_categories = relationship(
        "SkillCategory", back_populates="user", cascade="all, delete-orphan"
    )
    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    tailoring_runs = relationship(
        "TailoringRun", back_populates="user", cascade="all, delete-orphan"
    )
    resume_variants = relationship(
        "ResumeVariant", back_populates="user", cascade="all, delete-orphan"
    )


class Education(Base):
    __tablename__ = "education"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String)
    location = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    is_current = Column(Boolean, nullable=False, default=False, server_default="false")
    notes = Column(ARRAY(String))
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_archived = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="education")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    location = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    is_current = Column(Boolean, nullable=False, default=False, server_default="false")
    bullets = Column(ARRAY(String))
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_archived = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    subtitle = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    is_current = Column(Boolean, nullable=False, default=False, server_default="false")
    bullets = Column(ARRAY(String))
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_archived = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="projects")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    is_current = Column(Boolean, nullable=False, default=False, server_default="false")
    bullets = Column(ARRAY(String))
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_archived = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="activities")


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    skills = Column(ARRAY(String))
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    is_archived = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    archived_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="skill_categories")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    label = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(JSON, nullable=False)

    user = relationship("User", back_populates="resumes")


class TailoringRun(Base):
    __tablename__ = "tailoring_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    profile_version = Column(String(64), nullable=False)
    job_description = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending", server_default="pending")
    suggestions = Column(JSON, nullable=False, default=list, server_default="[]")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="tailoring_runs")
    variants = relationship("ResumeVariant", back_populates="tailoring_run")


class ResumeVariant(Base):
    __tablename__ = "resume_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tailoring_run_id = Column(
        UUID(as_uuid=True), ForeignKey("tailoring_runs.id"), nullable=True
    )
    label = Column(String, nullable=False)
    profile_version = Column(String(64), nullable=False)
    status = Column(String, nullable=False, default="draft", server_default="draft")
    document = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    approved_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="resume_variants")
    tailoring_run = relationship("TailoringRun", back_populates="variants")
