from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
import app.models
from app.models.user import User, UserProfile
from app.models.scheme import Scheme
from app.models.eligibility import EligibilityRule
from app.models.document import Document, DocumentChunk
from app.core.security import get_password_hash
import os
from dotenv import load_dotenv
load_dotenv()

from app.ingestion.embeddings import generate_embeddings
from app.rag.faiss_store import faiss_store

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 1. Create dummy user
user = db.query(User).filter(User.email == "test@example.com").first()
if not user:
    dummy_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq" 
    user = User(email="test@example.com", hashed_password=dummy_hash, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    from datetime import date
    profile = UserProfile(user_id=user.id, state="Telangana", date_of_birth=date(2000, 1, 1), annual_income=250000.0)
    db.add(profile)
    db.commit()

# 3. Create dummy scheme
scheme = db.query(Scheme).filter(Scheme.name == "Youth Employment Scheme").first()
if not scheme:
    scheme = Scheme(name="Youth Employment Scheme", department="Labor", state="Telangana", description="A scheme for youth employment.", is_active=True)
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    
    # 4. Create rule
    rule = EligibilityRule(scheme_id=scheme.id, rule_type="age", condition={"field": "age", "operator": ">=", "value": 18}, description="Age must be 18 or older.")
    db.add(rule)
    db.commit()

    # 5. Create Document and Chunks (Real Production Data seeding)
    doc = Document(scheme_id=scheme.id, filename="youth_emp_guidelines.pdf", file_type="pdf", status="COMPLETED")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    texts = [
        "The Youth Employment Scheme is designed for residents of Telangana to boost local hiring. It is managed by the Department of Labor.",
        "To be eligible for the scheme, applicants must be exactly 18 years of age or older. Their annual income must be below 3 Lakhs."
    ]
    
    # Generate REAL embeddings using OpenAI
    print("Generating real embeddings via OpenAI API...")
    embeddings = generate_embeddings(texts)
    
    chunk_ids = []
    for i, (text, emb) in enumerate(zip(texts, embeddings)):
        chunk = DocumentChunk(
            document_id=doc.id,
            scheme_id=scheme.id,
            text=text,
            page_number=1,
            section="Overview"
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        chunk_ids.append(chunk.id)
        
    # Index in FAISS
    faiss_store.add_embeddings(chunk_ids, embeddings)

print("Dummy data seeded with real embeddings in FAISS!")
