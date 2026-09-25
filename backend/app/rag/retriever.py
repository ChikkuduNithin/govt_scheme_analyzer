from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.document import DocumentChunk
from app.models.scheme import Scheme
from app.ingestion.embeddings import generate_embedding
from app.rag.faiss_store import faiss_store
from typing import List, Dict, Optional

def _format_results(scored_results: List, top_k: int) -> List[Dict]:
    retrieved = []
    for similarity, chunk, scheme in scored_results[:top_k]:
        retrieved.append({
            "chunk_id": chunk.id,
            "text": chunk.text,
            "scheme_id": chunk.scheme_id,
            "scheme_name": scheme.name,
            "department": scheme.department,
            "state": scheme.state,
            "page_number": chunk.page_number,
            "section": chunk.section,
            "similarity": similarity
        })
    return retrieved

def _retrieve_from_database(
    db: Session,
    query: str,
    state_filter: Optional[str],
    department_filter: Optional[str],
    scheme_id_filter: Optional[int],
    top_k: int,
) -> List[Dict]:
    words = [word.strip().lower() for word in query.split() if len(word.strip()) > 2]
    base_query = db.query(DocumentChunk, Scheme).join(Scheme, DocumentChunk.scheme_id == Scheme.id)
    filters = [Scheme.is_active == True]

    if state_filter:
        filters.append(or_(Scheme.state.ilike(f"%{state_filter}%"), Scheme.state.ilike("%central%")))
    if department_filter:
        filters.append(Scheme.department.ilike(f"%{department_filter}%"))
    if scheme_id_filter:
        filters.append(Scheme.id == scheme_id_filter)

    rows = base_query.filter(and_(*filters)).all()
    scored_results = []
    for chunk, scheme in rows:
        haystack = " ".join([
            scheme.name or "",
            scheme.department or "",
            scheme.state or "",
            scheme.description or "",
            chunk.text or "",
        ]).lower()
        score = sum(1 for word in words if word in haystack)
        if score > 0 or not words:
            scored_results.append((float(score), chunk, scheme))

    scored_results.sort(key=lambda item: item[0], reverse=True)
    return _format_results(scored_results, top_k)

def retrieve_hybrid(
    db: Session, 
    query: str, 
    state_filter: Optional[str] = None,
    department_filter: Optional[str] = None,
    scheme_id_filter: Optional[int] = None,
    top_k: int = 5
) -> List[Dict]:
    """
    Production-grade hybrid retrieval using FAISS for dense vector search
    and SQLite/SQLAlchemy for metadata filtering.
    """
    # 1. Embed the query
    query_vector = generate_embedding(query)

    if len(query_vector) != getattr(faiss_store.index, "d", len(query_vector)):
        return _retrieve_from_database(db, query, state_filter, department_filter, scheme_id_filter, top_k)
    
    # 2. Search FAISS for top 20 candidates (broad search before filtering)
    # If index is empty, this returns []
    try:
        faiss_results = faiss_store.search(query_vector, top_k=20)
    except Exception as exc:
        print(f"FAISS search unavailable, falling back to database search: {exc}")
        return _retrieve_from_database(db, query, state_filter, department_filter, scheme_id_filter, top_k)
    
    if not faiss_results:
        return _retrieve_from_database(db, query, state_filter, department_filter, scheme_id_filter, top_k)
        
    chunk_id_scores = {cid: score for cid, score in faiss_results}
    candidate_ids = list(chunk_id_scores.keys())
    
    if not candidate_ids: return []

    # 3. Apply DB metadata filters on the candidates
    base_query = db.query(DocumentChunk, Scheme).join(Scheme, DocumentChunk.scheme_id == Scheme.id)
    filters = [Scheme.is_active == True, DocumentChunk.id.in_(candidate_ids)]
    
    if state_filter:
        filters.append(or_(Scheme.state.ilike(f"%{state_filter}%"), Scheme.state.ilike("%central%")))
    if department_filter:
        filters.append(Scheme.department.ilike(f"%{department_filter}%"))
    if scheme_id_filter:
        filters.append(Scheme.id == scheme_id_filter)
        
    filtered_results = base_query.filter(and_(*filters)).all()
    
    # 4. Sort remaining candidates by FAISS similarity
    scored_results = []
    for chunk, scheme in filtered_results:
        scored_results.append((chunk_id_scores.get(chunk.id, 0.0), chunk, scheme))
        
    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_results[:top_k]
    
    return _format_results(top_results, top_k)
