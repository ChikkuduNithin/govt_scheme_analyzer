from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"
    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("scheme.id"))
    
    # Structured rule representation (e.g. {"field": "age", "operator": ">=", "value": 18})
    rule_type = Column(String) # e.g. age, income, state, category
    condition = Column(JSON) 
    description = Column(Text) # Plain English description of the rule
    
    scheme = relationship("Scheme", back_populates="rules")
