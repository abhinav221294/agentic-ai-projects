from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import IMAGE_PROMPT
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query
)

from src.integrations.image_client import generate_image

from src.tools.image_tools import image_generation_tool

from src.core.config import (
    IMAGE_GENERATED,
    IMAGE_COMPLETED,
    IMAGE_FAILED,
    IMAGE_VALIDATION_FAILED
)

import time

def image_agent(state: AgentState) -> AgentState:
    start = time.time()
    query = state.get("user_query")

    active_agent = "image_agent"

    if not validate_query(query):
        add_error(state, "Missing image query")
        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=0.2,
            agent=active_agent,
            trace_action=IMAGE_VALIDATION_FAILED,
            extra={
                 "workflow_step": IMAGE_VALIDATION_FAILED
            }
        )
    try:
        prompt = f"""{IMAGE_PROMPT}

User Query:
{query}""".strip()
        
        image_url = image_generation_tool.invoke(
        {"prompt": prompt}
        )
        

        add_trace(
            state,
            agent=active_agent,
            action=IMAGE_GENERATED
        )

        return set_state(
            state=state,
            start=start,
            answer=image_url,
            confidence=0.9,
            status="success",
            agent=active_agent,
            trace_action=IMAGE_GENERATED,
            extra={
                "image_prompt": prompt,
                "image_url": image_url,
                "workflow_step": IMAGE_COMPLETED
            }
    )

    except Exception as e:

        add_error(state, str(e))

        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=0.2,
            agent=active_agent,
            trace_action=IMAGE_FAILED,
            extra={
                "workflow_step": IMAGE_FAILED
            }
        )