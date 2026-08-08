import time
from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import BLOG_WRITER_PROMPT,GLOBAL_GUARDRAILS
from src.core.config import (BLOG_GENERATED ,BLOG_COMPLETED
,BLOG_GENERATION_FAILED,LOW_CONFIDENCE,HIGH_CONFIDENCE,
BLOG_STARTED,BLOG_STRUCTURE_GENERATED)
from src.integrations.claude_client import claude_client_llm
from src.tools.utility_tools import word_count_tool
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query,
    invoke_tool_with_trace
)

from src.tools.content_tools import (
    generate_title_tool,
    blog_outline_tool
)

from src.core.prompt_builder import build_prompt_context
from src.core.llm_service import LLMService

from dataclasses import dataclass
from typing import Any


@dataclass
class BlogGenerationContext:
    llm: Any
    prompt: str
    title: str
    outline: str
    active_agent: str

def prepare_blog_generation(state: AgentState) -> BlogGenerationContext:

    query = state.get("user_query")
    content_plan = state.get("content_plan")
    research_content = state.get("research_content", "")

    active_agent = "blog_writer_agent"

    context = build_prompt_context(state)

    if not validate_query(query):
        raise ValueError("Missing blog query")

    if not content_plan:
        raise ValueError("Missing content strategy")

    add_trace(
        state,
        agent=active_agent,
        action=BLOG_STARTED,
    )

    title = invoke_tool_with_trace(
        state=state,
        tool=generate_title_tool,
        tool_input={"topic": query},
        agent=active_agent,
        operation="generate_title"
    )

    outline = invoke_tool_with_trace(
        state=state,
        tool=blog_outline_tool,
        tool_input={"topic": query},
        agent=active_agent,
        operation="generate_outline"
    )

    research_section = (
        research_content
        if research_content
        else "No external research was performed."
    )

    add_trace(
        state,
        agent=active_agent,
        action=BLOG_STRUCTURE_GENERATED,
    )

    prompt = f"""{GLOBAL_GUARDRAILS}
{BLOG_WRITER_PROMPT}

{context}

Current User Query:
{query}

Suggested Title:
{title}

Suggested Outline:
{outline}

Research Context:
{research_section}

Content Strategy:
{content_plan}
"""

    llm = claude_client_llm(
        temperature=0.5,
        max_tokens=3500,
    )

    return BlogGenerationContext(
        llm=llm,
        prompt=prompt,
        title=title,
        outline=outline,
        active_agent=active_agent,
    )


def finalize_blog_generation(
    state: AgentState,
    ctx: BlogGenerationContext,
    blog_content: str,
    start: float,
) -> AgentState:

    word_count = word_count_tool.invoke(
        {"text": blog_content}
    )

    add_trace(
        state,
        agent=ctx.active_agent,
        action=BLOG_GENERATED,
    )

    execution_time = round(time.time() - start, 2)

    return set_state(
        state=state,
        answer=blog_content,
        confidence=HIGH_CONFIDENCE,
        status="success",
        agent=ctx.active_agent,
        trace_action=BLOG_GENERATED,
        extra={
            "title": ctx.title,
            "outline": ctx.outline,
            "word_count": word_count,
            "workflow_step": BLOG_COMPLETED,
            "execution_time": execution_time,
        },
    )

def blog_writer_agent(state: AgentState) -> AgentState:

    start = time.time()

    try:

        ctx = prepare_blog_generation(state)
        
        result = LLMService.invoke(
            llm=ctx.llm,
            prompt=ctx.prompt,
            state=state,
            agent=ctx.active_agent,
            operation="blog_generation"
        )
        metadata = getattr(
        result,
        "response_metadata",
        {}
        )

        print("\n========== LLM METADATA ==========")
        print(metadata)
        print("==================================\n")

        blog_content = result.content.strip()

        return finalize_blog_generation(
            state,
            ctx,
            blog_content,
            start,
        )

    except Exception as e:

        add_error(state, str(e))

        execution_time = round(time.time() - start, 2)

        return set_state(
            state=state,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent="blog_writer_agent",
            trace_action=BLOG_GENERATION_FAILED,
            extra={
                "workflow_step": BLOG_GENERATION_FAILED,
                "execution_time": execution_time,
            },
        )

def blog_writer_agent_stream(state: AgentState):

    start = time.time()

    try:

        ctx = prepare_blog_generation(state)

        blog_content = ""

        for chunk in LLMService.stream(
        ctx.llm,
        ctx.prompt,
        state=state,
        agent=ctx.active_agent,
        operation="blog_generation_stream",
        ):
            blog_content += chunk

            yield chunk
        # Save the completed state
        finalize_blog_generation(
            state,
            ctx,
            blog_content,
            start,
        )

    except Exception as e:

        add_error(state, str(e))

        raise