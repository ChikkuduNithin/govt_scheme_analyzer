from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str
    state_filter: Optional[str] = None
    department_filter: Optional[str] = None
    scheme_id_filter: Optional[int] = None
    
class SourceChunk(BaseModel):
    chunk_id: int
    text: str
    scheme_id: int
    scheme_name: str
    department: Optional[str] = None
    state: Optional[str] = None
    page_number: int
    section: str
    similarity: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
