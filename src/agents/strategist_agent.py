from src.workflows.state_management import AgentState, set_state
from src.prompts.prompt import CONTENT_STRATEGIST_PROMPT
from src.integrations.gemini_client import gemini_llm_client


def strategist_agent(state: AgentState) -> AgentState:
    
    research_content = state.get("answer")
    query = state.get("user_query")
    active_agent = "strategist_agent"
    category = state.get("category")

    prompt = f"""
{CONTENT_STRATEGIST_PROMPT}

User Query:
{query}

Research Content:
{research_content}"""
    
    try:
        llm = gemini_llm_client(temperature=0.2)
        response = llm.invoke(prompt)
        strategy = str(response.content).strip()
        status = "success"
        
        return set_state(
            state=state,
            category=category,
            confidence=0.9,
            status=status,
            agent=active_agent,
            trace_action="strategy_generated",
            extra={
                "content_plan": strategy,
                "workflow_step": "strategy_completed"
            }
        )

    except Exception as e:

        state["errors"].append(str(e))

        category = "none"
        status = "failed"
        

        return set_state(
            state=state,
            status="failed",
            agent=active_agent,
            confidence=0.2,
            trace_action="strategy_failed",
            extra={
                "workflow_step": "strategy_failed"
            }
        )
        


