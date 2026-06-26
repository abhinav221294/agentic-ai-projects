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
    validate_query
)

from src.core.config import (LINKEDIN_GENERATED,LINKEDIN_COMPLETED,
 LINKEDIN_VALIDATION_FAILED,LINKEDIN_FAILED,LOW_CONFIDENCE,HIGH_CONFIDENCE,
 LINKEDIN_STARTED,LINKEDIN_STRUCTURE_GENERATED)

def linkedin_writer_agent(state: AgentState) -> AgentState:
    start = time.time()
    query = state.get('user_query')
    content_plan = state.get("content_plan")
    active_agent = "linkedin_writer_agent"
    research_content = state.get(
    "research_content",
    ""
    )

    research_section = (
    research_content
    if research_content
    else "No external research was performed. Generate the LinkedIn post using your existing knowledge."
    )

    if not validate_query(query):
        add_error(state,"Missing LinkedIn query")
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent=active_agent,
            trace_action=LINKEDIN_VALIDATION_FAILED,
            extra={
                "workflow_step": LINKEDIN_VALIDATION_FAILED,
                 "execution_time": execution_time
            }
        )
    
    if not content_plan:

        add_error(state, "Missing content strategy")
        execution_time = round(time.time() - start, 2)
        return set_state(
        state=state,
        start=start,
        status="failed",
        confidence=LOW_CONFIDENCE,
        agent=active_agent,
        trace_action=LINKEDIN_VALIDATION_FAILED,
        extra={
            "workflow_step": LINKEDIN_VALIDATION_FAILED,
             "execution_time": execution_time
        }
    )
    try:
        add_trace(
            state,
            agent=active_agent,
            action=LINKEDIN_STARTED
        )
        hook = linkedin_hook_tool.invoke(
            {"topic":query}
        )

        cta = generate_cta_tool.invoke(
            {"content_type":"linkedin"}
        )

        add_trace(
            state,
            agent=active_agent,
            action=LINKEDIN_STRUCTURE_GENERATED
        )

        prompt = f"""{LINKEDIN_WRITER_PROMPT}

User Query:
{query}

Suggested Hook:
{hook}

Suggested CTA:
{cta}

Research Context:
{research_section}

Content Strategy:
{content_plan}"""
        
        llm  = claude_client_llm(
            temperature=0.6,
            max_tokens=1000,
        )

        response = llm.invoke(prompt)

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
            confidence=HIGH_CONFIDENCE,
            status="success",
            agent=active_agent,
            trace_action=LINKEDIN_GENERATED,
            extra={
                "hook":hook,
                "cta": cta,
                "word_count":word_count,
                "workflow_step": LINKEDIN_COMPLETED

                }
            )
    
    except Exception as e:
        add_error(state, str(e))
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            start=start,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent=active_agent,
            trace_action=LINKEDIN_FAILED,
            extra={
                "workflow_step": LINKEDIN_FAILED,
                 "execution_time": execution_time
            }
        )