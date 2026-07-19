import time
from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import BLOG_WRITER_PROMPT,GLOBAL_GUARDRAILS
from src.core.config import (BLOG_GENERATED ,BLOG_COMPLETED, 
BLOG_VALIDATION_FAILED,BLOG_GENERATION_FAILED,LOW_CONFIDENCE,HIGH_CONFIDENCE,
BLOG_STARTED,BLOG_STRUCTURE_GENERATED)
from src.integrations.claude_client import claude_client_llm
from src.tools.utility_tools import word_count_tool
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query
)
from src.tools.content_tools import (
    generate_title_tool,
    blog_outline_tool
)

from src.core.prompt_builder import build_prompt_context

def blog_writer_agent(state: AgentState) -> AgentState:
    start = time.time()
    query = state.get("user_query")
    content_plan = state.get("content_plan")
    research_content = state.get("research_content","")
    active_agent = "blog_writer_agent"
    context = build_prompt_context(state)
    if not validate_query(query):

        add_error(state, "Missing blog query")
        execution_time = round(time.time() - start, 2)
        return set_state(
        state=state,
        status="failed",
        confidence=LOW_CONFIDENCE,
        agent=active_agent,
        trace_action=BLOG_VALIDATION_FAILED,
        extra={
            "workflow_step": BLOG_VALIDATION_FAILED,
            "execution_time": execution_time
        }
        )
    
    if not content_plan:

        add_error(state, "Missing content strategy")

        execution_time = round(time.time() - start, 2)

        return set_state(
        state=state,
        status="failed",
        confidence=LOW_CONFIDENCE,
        agent=active_agent,
        trace_action=BLOG_VALIDATION_FAILED,
        extra={
            "workflow_step": BLOG_VALIDATION_FAILED,
            "execution_time": execution_time
            }
        )
 
    try:
        add_trace(
        state,
        agent=active_agent,
        action=BLOG_STARTED
        )
        title = generate_title_tool.invoke(
        {"topic": query}
        )

        outline = blog_outline_tool.invoke(
        {"topic": query}
        )
        research_section = (
            research_content
            if research_content
            else "No external research was performed. Generate the blog using your existing knowledge."
            )
        add_trace(
        state,
        agent=active_agent,
        action=BLOG_STRUCTURE_GENERATED
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
{content_plan}"""
        
        llm = claude_client_llm(temperature=0.5,max_tokens=3000)
        results = llm.invoke(prompt)

        print(results.response_metadata)

        blog_content = str(results.content).strip()
        
        word_count = word_count_tool.invoke(
        {"text": blog_content}
        )

        add_trace(
        state,
        agent=active_agent,
        action=BLOG_GENERATED
        )
        execution_time = round(time.time() - start, 2)
        return set_state(
        state=state,
        answer=blog_content,
        confidence=HIGH_CONFIDENCE,
        status="success",
        agent=active_agent,
        trace_action=BLOG_GENERATED,
        extra={
        "title": title,
        "outline": outline,
        "word_count": word_count,
        "workflow_step": BLOG_COMPLETED,
        "execution_time": execution_time
    }
)

    except Exception as e:
        add_error(state, str(e))
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            status="failed",
            confidence=LOW_CONFIDENCE,
            agent=active_agent,
            trace_action=BLOG_GENERATION_FAILED,
            extra={
                "workflow_step": BLOG_GENERATION_FAILED,
                "execution_time": execution_time
            }
        )
