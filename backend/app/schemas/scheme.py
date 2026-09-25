from pydantic import BaseModel
from typing import Optional
from datetime import date

class SchemeBase(BaseModel):
    name: str
    department: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    publication_date: Optional[date] = None
    last_updated_date: Optional[date] = None
    document_version: Optional[str] = None
    is_active: bool = True

class SchemeCreate(SchemeBase):
    pass

class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None

class Scheme(SchemeBase):
    id: int

    class Config:
        from_attributes = True
