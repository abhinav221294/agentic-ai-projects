from src.workflows.state_management import AgentState, set_state
from src.prompts.prompt import CONTENT_STRATEGIST_PROMPT
from src.core.config import (STRATEGY_COMPLETED ,STRATEGY_FAILED, STRATEGY_VALIDATION_FAILED, BLOG_VALIDATION_FAILED,
STRATEGY_GENERATED,STRATEGY_STARTED)
from src.integrations.gemini_client import gemini_llm_client
from src.core.workflow_utils import (
    add_trace,
    add_error
)
import time

def strategist_agent(state: AgentState) -> AgentState:
    start = time.time()
    research_content = state.get("answer")
    query = state.get("user_query")
    active_agent = "strategist_agent"

    if not research_content:

        add_error(state, "Missing research content")

        return set_state(
        state=state,
        status="failed",
        confidence=0.2,
        agent=active_agent,
        trace_action=STRATEGY_VALIDATION_FAILED,
        extra={
            "workflow_step": STRATEGY_VALIDATION_FAILED
        }
        )

    prompt = f"""
{CONTENT_STRATEGIST_PROMPT}

User Query:
{query}

Research Content:
{research_content}"""
    
    try:
        add_trace(
        state,
        agent=active_agent,
        action=STRATEGY_STARTED
        )

        llm = gemini_llm_client(temperature=0.2)
        response = llm.invoke(prompt)
        strategy = str(response.content).strip()
        status = "success"
        add_trace(
            state,
            agent=active_agent,
            action=STRATEGY_GENERATED
            )
        return set_state(
            state=state,
            confidence=0.9,
            status=status,
            agent=active_agent,
            trace_action=STRATEGY_GENERATED,
            extra={
                "content_plan": strategy,
                "workflow_step": STRATEGY_COMPLETED
            }
        )

    except Exception as e:

        add_error(state, str(e))

        return set_state(
            state=state,
            status="failed",
            agent=active_agent,
            confidence=0.2,
            trace_action=STRATEGY_FAILED,
            extra={
                "workflow_step": STRATEGY_FAILED
            }
        )
        


