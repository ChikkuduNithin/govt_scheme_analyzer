import traceback
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.document import Document, DocumentChunk
from app.ingestion.extractors import extract_text
from app.ingestion.chunkers import chunk_document
from app.ingestion.embeddings import generate_embeddings
from app.rag.faiss_store import faiss_store

def process_document(document_id: int, file_bytes: bytes, db: Optional[Session] = None):
    """
    Process an uploaded document: extract text, chunk, embed, and store in both SQL and FAISS.
    Uses its own isolated SessionLocal if db is not provided (safe for BackgroundTasks).
    """
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True
        
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            print(f"Document {document_id} not found.")
            return
        
        # Update status to PROCESSING
        document.status = "PROCESSING"
        db.commit()
        
        # 1. Extract text using real parsers
        text = extract_text(file_bytes, document.file_type)
        if not text:
            raise ValueError("Extracted text is empty.")
            
        # 2. Chunk text semantically
        chunks_data = chunk_document(text)
        if not chunks_data:
            raise ValueError("No chunks generated from document text.")
            
        # 3. Generate embeddings for all chunks in batches
        texts_to_embed = [c["text"] for c in chunks_data]
        embeddings = generate_embeddings(texts_to_embed)
        
        # 4. Save to SQL database
        chunk_ids = []
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
            db.commit()
            db.refresh(db_chunk)
            chunk_ids.append(db_chunk.id)
            
        # 5. Add to FAISS Vector Store
        faiss_store.add_embeddings(chunk_ids, embeddings)
        
        # Mark document as COMPLETED
        document.status = "COMPLETED"
        db.commit()
        print(f"Successfully processed document {document_id}: indexed {len(chunk_ids)} chunks into FAISS.")
        
    except Exception as e:
        print(f"Error processing document {document_id}: {e}")
        traceback.print_exc()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "FAILED"
                db.commit()
        except Exception:
            pass
    finally:
        if owns_session:
            db.close()
