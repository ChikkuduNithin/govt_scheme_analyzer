from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.query import QueryRequest, QueryResponse
from app.rag.retriever import retrieve_hybrid
from app.rag.generator import generate_answer
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=QueryResponse)
def handle_query(
    request: QueryRequest,
    db: Session = Depends(deps.get_db),
):
    """
    Hybrid RAG query endpoint. 
    Applies metadata filtering, embeds the query, searches pgvector, and generates a grounded response.
    """
    # 1. Retrieve chunks with hybrid search
    relevant_chunks = retrieve_hybrid(
        db=db,
        query=request.query,
        state_filter=request.state_filter,
        department_filter=request.department_filter,
        scheme_id_filter=request.scheme_id_filter,
        top_k=5
    )
    
    # 2. Generate answer
    answer = generate_answer(request.query, relevant_chunks)
    
    # 3. Return combined response
    return QueryResponse(
        answer=answer,
        sources=relevant_chunks
    )
