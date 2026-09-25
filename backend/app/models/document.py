from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Document(Base):
    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("scheme.id"))
    filename = Column(String)
    file_type = Column(String)  # pdf, docx, html
    status = Column(String)  # UPLOADED, PROCESSING, COMPLETED, FAILED, OUTDATED
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    scheme = relationship("Scheme", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id"))
    scheme_id = Column(Integer, ForeignKey("scheme.id"))
    
    # Text and vector
    text = Column(Text, nullable=False)
    embedding = Column(JSON)  # Store embedding as JSON list instead of pgvector
    
    # Metadata
    page_number = Column(Integer)
    section = Column(String)
    
    document = relationship("Document", back_populates="chunks")
