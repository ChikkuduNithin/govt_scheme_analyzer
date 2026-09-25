from sqlalchemy import Column, Integer, String, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Scheme(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    department = Column(String, index=True)
    state = Column(String, index=True)  # 'Central' or specific state name
    description = Column(Text)
    source_url = Column(String)
    publication_date = Column(Date)
    last_updated_date = Column(Date)
    document_version = Column(String)
    is_active = Column(Boolean, default=True)
    
    documents = relationship("Document", back_populates="scheme")
    rules = relationship("EligibilityRule", back_populates="scheme")
