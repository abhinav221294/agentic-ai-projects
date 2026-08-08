import time
from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import LINKEDIN_WRITER_PROMPT,GLOBAL_GUARDRAILS
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
    invoke_tool_with_trace
)

from src.core.config import (LINKEDIN_GENERATED,LINKEDIN_COMPLETED,
LINKEDIN_FAILED,LOW_CONFIDENCE,HIGH_CONFIDENCE,
 LINKEDIN_STARTED,LINKEDIN_STRUCTURE_GENERATED)

from src.core.prompt_builder import build_prompt_context
from src.core.llm_service import LLMService

from dataclasses import dataclass
from typing import Any


@dataclass
class LinkedInGenerationContext:
    llm: Any
    prompt: str
    hook: str
    cta: str
    active_agent: str


def prepare_linkedin_generation(
    state: AgentState,
) -> LinkedInGenerationContext:

    query = state.get("user_query")
    content_plan = state.get("content_plan")
    research_content = state.get("research_content", "")

    active_agent = "linkedin_writer_agent"

    context = build_prompt_context(state)

    if not validate_query(query):
        raise ValueError("Missing LinkedIn query")

    if not content_plan:
        raise ValueError("Missing content strategy")

    research_section = (
        research_content
        if research_content
        else "No external research was performed. Generate the LinkedIn post using your existing knowledge."
    )

    add_trace(
        state,
        agent=active_agent,
        action=LINKEDIN_STARTED,
    )

    hook = invoke_tool_with_trace(
        state=state,
        tool=linkedin_hook_tool,
        tool_input={"topic": query},
        agent=active_agent,
        operation="generate_hook"
    )

    cta = generate_cta_tool.invoke(
        {"content_type": "linkedin"}
    )

    add_trace(
        state,
        agent=active_agent,
        action=LINKEDIN_STRUCTURE_GENERATED,
    )

    prompt = f"""{GLOBAL_GUARDRAILS}
{LINKEDIN_WRITER_PROMPT}

{context}

Current User Query:
{query}

Suggested Hook:
{hook}

Suggested CTA:
{cta}

Research Context:
{research_section}

Content Strategy:
{content_plan}
"""

    llm = claude_client_llm(
        temperature=0.6,
        max_tokens=1000,
    )

    return LinkedInGenerationContext(
        llm=llm,
        prompt=prompt,
        hook=hook,
        cta=cta,
        active_agent=active_agent,
    )

def finalize_linkedin_generation(
    state: AgentState,
    ctx: LinkedInGenerationContext,
    linkedin_post: str,
    start: float,
) -> AgentState:

    word_count = word_count_tool.invoke(
        {"text": linkedin_post}
    )

    add_trace(
        state,
        agent=ctx.active_agent,
        action=LINKEDIN_GENERATED,
    )

    execution_time = round(time.time() - start, 2)

    return set_state(
        state=state,
        answer=linkedin_post,
        confidence=HIGH_CONFIDENCE,
        status="success",
        agent=ctx.active_agent,
        trace_action=LINKEDIN_GENERATED,
        extra={
            "hook": ctx.hook,
            "cta": ctx.cta,
            "word_count": word_count,
            "workflow_step": LINKEDIN_COMPLETED,
            "execution_time": execution_time,
        },
    )

def linkedin_writer_agent(state: AgentState) -> AgentState:

    start = time.time()

    try:

        ctx = prepare_linkedin_generation(state)

        result = LLMService.invoke(
            llm=ctx.llm,
            prompt=ctx.prompt,
            state=state,
            agent=ctx.active_agent,
            operation="linkedin_generation",
        )

        metadata = getattr(
        result,
        "response_metadata",
        {}
        )

        print("\n========== LLM METADATA ==========")
        print(metadata)
        print("==================================\n")

        linkedin_post = result.content.strip()

        return finalize_linkedin_generation(
            state,
            ctx,
            linkedin_post,
            start,
        )

    except Exception as e:

        add_error(state, str(e))

        execution_time = round(time.time() - start, 2)

        return set_state(
            state=state,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent="linkedin_writer_agent",
            trace_action=LINKEDIN_FAILED,
            extra={
                "workflow_step": LINKEDIN_FAILED,
                "execution_time": execution_time,
            },
        )
    
def linkedin_writer_agent_stream(state: AgentState):

    start = time.time()

    try:

        ctx = prepare_linkedin_generation(state)

        linkedin_post = ""

        for chunk in LLMService.stream(
        ctx.llm,
        ctx.prompt,
        state=state,
        agent=ctx.active_agent,
        operation="linkedin_generation_stream",
        ):
            linkedin_post += chunk
            yield chunk

        finalize_linkedin_generation(
            state,
            ctx,
            linkedin_post,
            start,
        )

    except Exception as e:

        add_error(state, str(e))
        raise
