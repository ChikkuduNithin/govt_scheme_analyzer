from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from app.agents.state import AgentState
from app.agents.nodes import coordinator_node, get_retrieval_node, get_eligibility_node
from app.agents.verification_node import verification_node

def create_agent_workflow(db: Session):
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("retriever", get_retrieval_node(db))
    workflow.add_node("eligibility_engine", get_eligibility_node(db))
    workflow.add_node("verification", verification_node)
    
    # Define edges
    workflow.set_entry_point("coordinator")
    workflow.add_edge("coordinator", "retriever")
    workflow.add_edge("retriever", "eligibility_engine")
    workflow.add_edge("eligibility_engine", "verification")
    workflow.add_edge("verification", END)
    
    return workflow.compile()
