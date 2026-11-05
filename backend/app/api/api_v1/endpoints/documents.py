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
    """Upload a government scheme document and process it in background (Admin only)."""
    # Verify scheme exists
    scheme = scheme_service.get_scheme(db, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    # Validate file type
    filename = file.filename or "uploaded_document.pdf"
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if ext not in ['pdf', 'docx', 'doc', 'html', 'txt']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, HTML, or TXT.")
        
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
    
    # Process offline with a fresh isolated session inside the worker
    background_tasks.add_task(process_document, db_document.id, file_bytes)
    
    return {
        "message": "Document uploaded and processing started.",
        "document_id": db_document.id,
        "scheme_id": scheme_id
    }

@router.get("/")
def list_documents(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """List all documents and their status (Admin only)."""
    docs = db.query(Document).offset(skip).limit(limit).all()
    return [{"id": d.id, "filename": d.filename, "status": d.status, "scheme_id": d.scheme_id, "file_type": d.file_type} for d in docs]
