from src.workflows.state_management import AgentState

def create_initial_state(
    query: str,
    conversation_id: str,
    user_id: str = "demo_user"
) -> AgentState:

    return {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "user_query": query,

        "messages": [],
        "conversation_history": [],

        "retrieved_memories": [],
        "memory": [],
        "user_preferences": {},

        "trace": [],
        "errors": [],

        "status": "running"
    }