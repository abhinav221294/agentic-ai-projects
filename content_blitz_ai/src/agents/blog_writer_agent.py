import time
from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import BLOG_WRITER_PROMPT
from src.core.config import (BLOG_GENERATED ,BLOG_COMPLETED, BLOG_FAILED, BLOG_VALIDATION_FAILED,
BLOG_GENERATION_FAILED)
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

def blog_writer_agent(state: AgentState) -> AgentState:
    start = time.time()
    query = state.get("user_query")
    content_plan = state.get("content_plan")
    active_agent = "blog_writer_agent"
    if not validate_query(query):

        add_error(state, "Missing blog query")

        return set_state(
        state=state,
        status="failed",
        confidence=0.2,
        agent=active_agent,
        trace_action=BLOG_VALIDATION_FAILED,
        extra={
            "workflow_step": BLOG_VALIDATION_FAILED
        }
        )
 
    try:
        title = generate_title_tool.invoke(
        {"topic": query}
        )

        outline = blog_outline_tool.invoke(
        {"topic": query}
        )
        prompt = f"""{BLOG_WRITER_PROMPT}

User Query:
{query}

Suggested Title:
{title}

Suggested Outline:
{outline}

Content Strategy:
{content_plan}"""
        
        llm = claude_client_llm(temperature=0.5,max_tokens=2000)
        results = llm.invoke(prompt)
        blog_content = str(results.content).strip()
        
        word_count = word_count_tool.invoke(
        {"text": blog_content}
        )

        add_trace(
        state,
        agent=active_agent,
        action=BLOG_GENERATED
        )

        return set_state(
        state=state,
        answer=blog_content,
        confidence=0.9,
        status="success",
        agent=active_agent,
        trace_action=BLOG_GENERATED,
        extra={
        "title": title,
        "outline": outline,
        "word_count": word_count,
        "blog_content": blog_content,
        "workflow_step": BLOG_COMPLETED
    }
)

    except Exception as e:
        add_error(state, str(e))

        return set_state(
            state=state,
            status="failed",
            confidence=0.2,
            agent=active_agent,
            trace_action=BLOG_GENERATION_FAILED,
            extra={
                "workflow_step": BLOG_FAILED
            }
        )
