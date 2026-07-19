from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import IMAGE_PROMPT,GLOBAL_GUARDRAILS
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query
)

from src.tools.image_tools import image_generation_tool

from src.core.config import (
    IMAGE_STARTED,
    IMAGE_GENERATED,
    IMAGE_COMPLETED,
    IMAGE_FAILED,
    IMAGE_VALIDATION_FAILED,
    LOW_CONFIDENCE,
    HIGH_CONFIDENCE
)

import time

def image_agent(state: AgentState) -> AgentState:
    start = time.time()
    query = state.get("user_query")

    active_agent = "image_agent"
  
    if not validate_query(query):
        add_trace(
        state,
        agent=active_agent,
        action=IMAGE_VALIDATION_FAILED
        )
        add_error(state, "Missing image query")
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent=active_agent,
            trace_action=IMAGE_VALIDATION_FAILED,
            extra={
                 "workflow_step": IMAGE_VALIDATION_FAILED,
                 "execution_time": execution_time
            }
        )
    try:
        add_trace(
            state,
            agent=active_agent,
            action=IMAGE_STARTED
         )
        
        prompt = f"""{GLOBAL_GUARDRAILS}

{IMAGE_PROMPT}

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
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            start=start,
            answer=image_url,
            confidence=HIGH_CONFIDENCE,
            status="success",
            agent=active_agent,
            trace_action=IMAGE_GENERATED,
            extra={
                "image_prompt": prompt,
                "image_url": image_url,
                "workflow_step": IMAGE_COMPLETED,
                "execution_time": execution_time
            }
    )

    except Exception as e:

        add_error(state, str(e))
        add_trace(
        state,
        agent=active_agent,
        action=IMAGE_FAILED
        )
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent=active_agent,
            trace_action=IMAGE_FAILED,
            extra={
                "workflow_step": IMAGE_FAILED,
                "execution_time": execution_time
            }
        )