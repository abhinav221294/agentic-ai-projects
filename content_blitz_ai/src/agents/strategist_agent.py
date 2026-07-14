from src.workflows.state_management import AgentState, set_state
from src.prompts.prompt import CONTENT_STRATEGIST_PROMPT,GLOBAL_GUARDRAILS
from src.core.config import (STRATEGY_COMPLETED ,STRATEGY_FAILED, STRATEGY_VALIDATION_FAILED, BLOG_VALIDATION_FAILED,
STRATEGY_GENERATED,STRATEGY_STARTED,HIGH_CONFIDENCE,LOW_CONFIDENCE)
from src.integrations.gemini_client import gemini_llm_client
from src.core.workflow_utils import (
    add_trace,
    add_error
)
import time

def strategist_agent(state: AgentState) -> AgentState:
    start = time.time()
    research_content = state.get("research_content", "")
    query = state.get("user_query","")
    active_agent = "strategist_agent"

    if not query:

        add_error(state, "Missing user query")

        return set_state(
        state=state,
        status="failed",
        confidence=LOW_CONFIDENCE,
        agent=active_agent,
        trace_action=STRATEGY_VALIDATION_FAILED,
        extra={
            "workflow_step": STRATEGY_VALIDATION_FAILED
        }
    )

    research_section = (
    research_content
    if research_content
    else "No external research was performed. Create the strategy using your own knowledge."
    )

    prompt = f"""{GLOBAL_GUARDRAILS}
{CONTENT_STRATEGIST_PROMPT}

User Query:
{query}

Research Context:
{research_section}"""
    
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
        execution_time = round(time.time() - start, 2)
        add_trace(
            state,
            agent=active_agent,
            action=STRATEGY_GENERATED
            )
        return set_state(
            state=state,
            confidence=HIGH_CONFIDENCE,
            status=status,
            agent=active_agent,
            trace_action=STRATEGY_GENERATED,
            extra={
                "content_plan": strategy,
                "workflow_step": STRATEGY_COMPLETED,
                "execution_time": execution_time
            }
        )

    except Exception as e:

        add_error(state, str(e))
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            status="failed",
            agent=active_agent,
            confidence=LOW_CONFIDENCE,
            trace_action=STRATEGY_FAILED,
            extra={
                "workflow_step": STRATEGY_FAILED,
                "execution_time": execution_time
            }
        )
        


