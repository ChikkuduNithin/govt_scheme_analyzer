from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os

from app.db.session import get_db
from app.models.scheme import Scheme
from app.models.eligibility import EligibilityRule
from app.models.document import Document, DocumentChunk
from app.ingestion.embeddings import generate_embeddings
from app.rag.faiss_store import faiss_store

# Mock imports for extraction/chunking
# In production, use PyMuPDF and Langchain text splitters
def extract_text_mock(file_path: str) -> str:
    # Basic mock for now - you'd replace with real PyMuPDF extraction
    return "This is mock extracted text from the uploaded PDF detailing the scheme."

def chunk_text_mock(text: str) -> List[str]:
    # Mock chunking
    return [text[i:i+500] for i in range(0, len(text), 500)]

router = APIRouter()

class RuleCreate(BaseModel):
    rule_type: str
    field: str
    operator: str
    value: str
    description: str

class SchemeCreate(BaseModel):
    name: str
    department: str
    state: str
    description: str
    rules: List[RuleCreate]

@router.post("/schemes/")
def create_scheme(scheme_in: SchemeCreate, db: Session = Depends(get_db)):
    # Create Scheme
    scheme = Scheme(
        name=scheme_in.name,
        department=scheme_in.department,
        state=scheme_in.state,
        description=scheme_in.description,
        is_active=True
    )
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    
    # Create Rules
    for r in scheme_in.rules:
        # Try to parse value to int/float if possible
        val = r.value
        try:
            if "." in val:
                val = float(val)
            else:
                val = int(val)
        except:
            if "," in val:
                val = [v.strip() for v in val.split(",")]
                
        rule = EligibilityRule(
            scheme_id=scheme.id,
            rule_type=r.rule_type,
            condition={"field": r.field, "operator": r.operator, "value": val},
            description=r.description
        )
        db.add(rule)
    db.commit()
    return {"message": "Scheme created successfully", "scheme_id": scheme.id}


def process_document_background(db: Session, scheme_id: int, doc_id: int, file_path: str):
    try:
        # 1. Extract Text
        text = extract_text_mock(file_path)
        
        # 2. Chunk
        chunks_text = chunk_text_mock(text)
        
        # 3. Embed
        embeddings = generate_embeddings(chunks_text)
        
        # 4. Save to DB and FAISS
        chunk_ids = []
        for i, chunk_txt in enumerate(chunks_text):
            chunk = DocumentChunk(
                document_id=doc_id,
                scheme_id=scheme_id,
                text=chunk_txt,
                page_number=1,
                section=f"Section {i+1}"
            )
            db.add(chunk)
            db.commit()
            db.refresh(chunk)
            chunk_ids.append(chunk.id)
            
        faiss_store.add_embeddings(chunk_ids, embeddings)
        
        # Update Doc Status
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.status = "COMPLETED"
        db.commit()
        
    except Exception as e:
        print(f"Error processing document: {e}")
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.status = "FAILED"
        db.commit()

@router.post("/schemes/{scheme_id}/documents/")
def upload_scheme_document(
    scheme_id: int, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    # Save file locally
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{scheme_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create DB Entry
    doc = Document(
        scheme_id=scheme.id,
        filename=file.filename,
        file_type="pdf",
        status="PROCESSING"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Process in background (Production strategy step 2)
    background_tasks.add_task(process_document_background, db, scheme.id, doc.id, file_path)
    
    return {"message": "Document uploaded and processing started in background", "document_id": doc.id}
