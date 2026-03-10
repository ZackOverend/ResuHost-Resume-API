from sqlalchemy import Column, Integer, String, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    summary = Column(Text)
    skills = Column(ARRAY(String))
    
    experiences = relationship("Experience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    start_date = Column(String)
    end_date = Column(String)
    description = Column(ARRAY(String))
    
    user = relationship("User", back_populates="experiences")

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    institution = Column(String, nullable=False)
    degree = Column(String)
    field = Column(String)
    graduation_date = Column(String)
    
    user = relationship("User", back_populates="education")