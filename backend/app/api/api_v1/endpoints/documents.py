from typing import Any, List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.document import Document
from app.services import scheme_service
from app.ingestion.pipeline import process_document

router = APIRouter()

@router.post("/upload/{scheme_id}")
async def upload_document(
    scheme_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
) -> Any:
    """Upload a government scheme document (Admin only)."""
    # Verify scheme exists
    scheme_service.get_scheme(db, scheme_id)
    
    # Validate file type
    filename = file.filename
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext not in ['pdf', 'docx', 'html']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or HTML.")
        
    # Create document record
    db_document = Document(
        scheme_id=scheme_id,
        filename=filename,
        file_type=ext,
        status="UPLOADED"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Process offline
    background_tasks.add_task(process_document, db, db_document.id, file_bytes)
    
    return {"message": "Document uploaded and processing started.", "document_id": db_document.id}

@router.get("/")
def list_documents(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """List all documents and their status (Admin only)."""
    docs = db.query(Document).offset(skip).limit(limit).all()
    # Simple dict conversion for now
    return [{"id": d.id, "filename": d.filename, "status": d.status, "scheme_id": d.scheme_id} for d in docs]
