from src.integrations.gemini_client import gemini_llm_client
from src.workflows.state_management import AgentState
from src.prompts.prompt import RESEARCH_DECISION_PROMPT


def research_decision_agent(state: AgentState):

    try:
        query = state.get("user_query")

        prompt = f"""
{RESEARCH_DECISION_PROMPT}

User Query:
{query}
"""

        llm = gemini_llm_client(temperature=0,max_tokens=5)

        response = llm.invoke(prompt)

        decision = str(
            response.content
        ).strip().upper()

        state["requires_research"] = (
            decision == "RESEARCH"
        )

        return state

    except Exception:
        state["requires_research"] = False
        return state
