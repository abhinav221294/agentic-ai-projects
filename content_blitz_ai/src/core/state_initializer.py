from src.workflows.state_management import AgentState

def create_initial_state(query: str) -> AgentState:
    return {
        "user_id": "demo_user",
        "session_id": "session_001",
        "user_query": query,
        "conversation_history": [],
        "memory": [],
        "errors": [],
        "trace": []
    }