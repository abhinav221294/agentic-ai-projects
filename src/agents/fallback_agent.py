from src.workflows.state_management import AgentState, set_state

import time


def fallback_agent(state: AgentState) -> AgentState:

    start = time.time()

    active_agent = "fallback_agent"

    fallback_message = """Sorry, I could not understand the request properly.

Please try asking for:
- blog generation
- linkedin post
- research
- image generation
- strategy"""

    return set_state(
        state=state,
        start=start,
        answer=fallback_message,
        confidence=0.2,
        status="success",
        agent=active_agent,
        trace_action="fallback_response",
        extra={
            "workflow_step": "fallback_completed"
        }
    )