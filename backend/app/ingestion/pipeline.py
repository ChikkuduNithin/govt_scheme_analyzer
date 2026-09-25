from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.ingestion.extractors import extract_text
from app.ingestion.chunkers import chunk_document
from app.ingestion.embeddings import generate_embeddings
import traceback

def process_document(db: Session, document_id: int, file_bytes: bytes):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return
    
    try:
        # Update status
        document.status = "PROCESSING"
        db.commit()
        
        # 1. Extract text
        text = extract_text(file_bytes, document.file_type.lower())
        
        # 2. Chunk text and extract metadata
        chunks_data = chunk_document(text)
        
        # 3. Generate embeddings for all chunks in batches
        texts_to_embed = [c["text"] for c in chunks_data]
        embeddings = generate_embeddings(texts_to_embed)
        
        # 4. Save to database
        for idx, chunk_info in enumerate(chunks_data):
            db_chunk = DocumentChunk(
                document_id=document.id,
                scheme_id=document.scheme_id,
                text=chunk_info["text"],
                page_number=chunk_info["page_number"],
                section=chunk_info["section"],
                embedding=embeddings[idx]
            )
            db.add(db_chunk)
            
        document.status = "COMPLETED"
        db.commit()
        
    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
        traceback.print_exc()
        document.status = "FAILED"
        db.commit()
