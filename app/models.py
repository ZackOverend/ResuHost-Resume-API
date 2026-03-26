from sqlalchemy import Column, Integer, String, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    linkedin = Column(String)
    website = Column(String)

    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    skill_categories = relationship("SkillCategory", back_populates="user", cascade="all, delete-orphan")


class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String)
    location = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    notes = Column(ARRAY(String))

    user = relationship("User", back_populates="education")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    location = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    bullets = Column(ARRAY(String))

    user = relationship("User", back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    subtitle = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    bullets = Column(ARRAY(String))

    user = relationship("User", back_populates="projects")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    bullets = Column(ARRAY(String))

    user = relationship("User", back_populates="activities")


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    skills = Column(ARRAY(String))

    user = relationship("User", back_populates="skill_categories")
