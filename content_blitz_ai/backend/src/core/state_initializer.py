from src.workflows.state_management import AgentState
import uuid

def create_initial_state(
    query: str,
    conversation_id: str,
    user_id: str = "demo_user",
    trace_id: str = None,
) -> AgentState:
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    return {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "user_query": query,

        "messages": [],
        "conversation_history": [],

        "retrieved_memories": [],
        "memory": [],
        "user_preferences": {},
        "trace_id": trace_id,
        "trace": [],
        "errors": [],

        "status": "running"
    }