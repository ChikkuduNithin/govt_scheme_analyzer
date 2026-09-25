from pydantic import BaseModel
from typing import Optional
from datetime import date

# User Base
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

# User Profile Base
class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    annual_income: Optional[float] = None
    occupation: Optional[str] = None
    employment_status: Optional[str] = None
    education_level: Optional[str] = None
    category: Optional[str] = None
    disability_status: Optional[bool] = False

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
