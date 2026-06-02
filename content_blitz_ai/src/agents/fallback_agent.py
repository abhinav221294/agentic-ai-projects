from src.workflows.state_management import AgentState, set_state
from src.core.config import FALLBACK_STARTED,FALLBACK_COMPLETED,FALLBACK_RESPONSE
import time
from src.core.workflow_utils import (
    add_trace,
    calculate_execution_time
)

def fallback_agent(state: AgentState) -> AgentState:

    start = time.time()

    active_agent = "fallback_agent"
    answer=FALLBACK_RESPONSE

    add_trace(
    state,
    agent=active_agent,
    action=FALLBACK_STARTED
    )

    return set_state(
    state=state,
    start=start,
    answer=answer,
    confidence=0.2,
    status="success",
    agent=active_agent,
    trace_action=FALLBACK_RESPONSE,
    extra={
        "workflow_step": FALLBACK_COMPLETED,
        "execution_time": calculate_execution_time(start)
    }
)