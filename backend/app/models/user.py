from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True)
    
    # Demographics
    full_name = Column(String)
    date_of_birth = Column(Date)
    gender = Column(String) # Male, Female, Other
    
    # Location
    state = Column(String, index=True)
    district = Column(String)
    
    # Socio-economic
    annual_income = Column(Float)
    occupation = Column(String)
    employment_status = Column(String) # Unemployed, Employed, Self-employed, Student
    education_level = Column(String)
    category = Column(String) # General, OBC, SC, ST
    disability_status = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="profile")
