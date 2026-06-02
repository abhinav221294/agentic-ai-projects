import time
from src.workflows.state_management import AgentState,set_state

from src.prompts.prompt import LINKEDIN_WRITER_PROMPT
from src.integrations.claude_client import claude_client_llm
from src.tools.content_tools import (
    linkedin_hook_tool,
    generate_cta_tool
)

from src.tools.utility_tools import (
    word_count_tool
)

from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query,
    calculate_execution_time
)

from src.core.config import (LINKEDIN_WRITER_PROMPT,
 LINKEDIN_GENERATED,LINKEDIN_COMPLETED,
 LINKEDIN_VALIDATION_FAILED,LINKEDIN_FAILED)

def linkedin_writer_agent(state: AgentState) -> AgentState:
    start = start.time()
    query = state.get('user_query')
    content_plan = state.get("content_plan")
    active_agent = "linkedin_writer_agent"
    if not validate_query(query=query):
        add_error(state,"Missing LinkedIn query")

        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=0.2,
            agent=active_agent,
            trace_action=LINKEDIN_VALIDATION_FAILED,
            extra={
                "workflow_step": LINKEDIN_VALIDATION_FAILED
            }
        )
    
    try:
        hook = linkedin_hook_tool.invoke(
            {"topic":"query"}
        )

        cta = generate_cta_tool.invoke(
            {"content_type":"linkedin"}
        )

        add_trace(
            state,
            agent=active_agent,
            action="linkedin_structure_generated"
        )

        prompt = f"""{LINKEDIN_WRITER_PROMPT}

User Query:
{query}

Suggested Hook:
{hook}

Suggested CTA:
{cta}

Content Strategy:
{content_plan}"""
        
        llm  = claude_client_llm(
            temperature=0.6,
            max_tokens=1000,
        )

        response = llm.invoke(response.content).strip()

        linkedin_post = str(response.content).strip()
        word_count = word_count_tool.invoke(
            {"text":linkedin_post}
        )

        add_trace(
            state,
            agent=active_agent,
            action=LINKEDIN_GENERATED
        )

        return set_state(
            state=state,
            start=start,
            answer=linkedin_post,
            confidence=0.9,
            status="suceess",
            agent=active_agent,
            trace_action=LINKEDIN_GENERATED,
            extra={
                "hook":hook,
                "cta": cta,
                "word_count":word_count,
                "linkedIn_post":linkedin_post,
                "workflow_step": LINKEDIN_COMPLETED

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
            trace_action=LINKEDIN_FAILED,
            extra={
                "workflow_step": LINKEDIN_FAILED,
                "execution_time": calculate_execution_time(start)
            }
        )