# src/test_trace.py

from src.core.state_initializer import create_initial_state
from src.core.workflow_utils import add_trace

state = create_initial_state(
    query="Test query",
    conversation_id="1",
)

print("TRACE ID:", state["trace_id"])

add_trace(
    state,
    agent="test_agent",
    action="test_action",
)

print("\nTRACE:")
print(state["trace"])