from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import BLOG_WRITER_PROMPT
from src.integrations.claude_client import claude_client_llm
from src.integrations.gemini_client import gemini_llm_client

def blog_writer_agent(state: AgentState) -> AgentState:
    query = state.get("user_query")
    content_plan = state.get("content_plan")
    active_agent = "blog_writer_agent"

    prompt = f"""
{BLOG_WRITER_PROMPT}

User Query:
{query}

Content Strategy:
{content_plan}"""
    
    try:
        llm = claude_client_llm(temperature=0.5,max_tokens=2000)
        results = llm.invoke(prompt)
        blog_content = str(results.content).strip()

        return set_state(state=state,
                         answer=blog_content,
                         confidence=0.9,
                         status="success",
                         agent=active_agent,
                         trace_action="blog_generated",
                         extra={
                        "blog_content": blog_content,
                         "workflow_step": "blog_completed"
                        }
                         )

    except Exception as e:

        state["errors"].append(str(e))

        return set_state(
            state=state,
            status="failed",
            confidence=0.2,
            agent=active_agent,
            trace_action="blog_generation_failed",
            extra={
                "workflow_step": "blog_failed"
            }
        )
