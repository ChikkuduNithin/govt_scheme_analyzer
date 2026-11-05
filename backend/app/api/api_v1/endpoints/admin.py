from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any
import shutil
import os

from app.api import deps
from app.models.scheme import Scheme
from app.models.eligibility import EligibilityRule
from app.models.document import Document
from app.models.user import User
from app.ingestion.pipeline import process_document

router = APIRouter()

class RuleCreate(BaseModel):
    rule_type: str
    field: str
    operator: str
    value: Any
    description: str

class SchemeCreate(BaseModel):
    name: str
    department: str
    state: str
    description: str
    rules: Optional[List[RuleCreate]] = []

@router.post("/schemes/")
def create_scheme(
    scheme_in: SchemeCreate, 
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_active_user)
):
    """Create a new government scheme with structured mathematical eligibility rules."""
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
    created_rules = []
    if scheme_in.rules:
        for r in scheme_in.rules:
            val = r.value
            # Type cast strings to numbers/lists if needed
            if isinstance(val, str):
                try:
                    if "." in val:
                        val = float(val)
                    else:
                        val = int(val)
                except ValueError:
                    if "," in val:
                        val = [v.strip() for v in val.split(",")]
                    elif val.lower() == "true":
                        val = True
                    elif val.lower() == "false":
                        val = False
                        
            rule = EligibilityRule(
                scheme_id=scheme.id,
                rule_type=r.rule_type,
                condition={"field": r.field, "operator": r.operator, "value": val},
                description=r.description
            )
            db.add(rule)
            created_rules.append(rule)
        db.commit()
        
    return {
        "message": "Scheme created successfully", 
        "scheme_id": scheme.id,
        "rules_count": len(created_rules)
    }

@router.post("/schemes/{scheme_id}/documents/")
async def upload_scheme_document(
    scheme_id: int, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_active_user)
):
    """Upload PDF/document for a scheme and trigger real background ingestion into FAISS."""
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    filename = file.filename or "uploaded.pdf"
    ext = filename.split('.')[-1].lower() if '.' in filename else 'pdf'
    
    # Read bytes
    file_bytes = await file.read()
    
    # Create DB Entry
    doc = Document(
        scheme_id=scheme.id,
        filename=filename,
        file_type=ext,
        status="UPLOADED"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Process using the real pipeline in background (isolated session)
    background_tasks.add_task(process_document, doc.id, file_bytes)
    
    return {
        "message": "Document uploaded and processing started in background", 
        "document_id": doc.id,
        "scheme_id": scheme.id
    }
