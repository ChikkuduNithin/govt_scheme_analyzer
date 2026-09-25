from typing import TypedDict, List, Dict, Any, Optional
from app.models.user import UserProfile

class AgentState(TypedDict):
    # Inputs
    user_query: str
    user_profile: Optional[UserProfile]
    
    # Extracted by Coordinator
    extracted_intent: str
    search_keywords: str
    state_filter: Optional[str]
    department_filter: Optional[str]
    
    # Retrieved by Retrieval Agent
    retrieved_chunks: List[Dict]
    
    # Evaluated by Eligibility Engine
    eligibility_results: Dict[int, Dict]  # scheme_id -> evaluation result
    
    # Final Output
    final_response: str
