from src.core.llm_service import LLMService
from src.integrations.gemini_client import gemini_llm_client
from src.workflows.state_management import AgentState
from src.prompts.prompt import RESEARCH_DECISION_PROMPT,GLOBAL_GUARDRAILS
from src.core.config import GEMINI_MODEL


#def research_decision_agent(state: AgentState):
#
#    try:
#        query = state.get("user_query")
#
#        prompt = f"""{GLOBAL_GUARDRAILS}
#
#{RESEARCH_DECISION_PROMPT}
#
#User Query:
#{query}
#"""
#
#        llm = gemini_llm_client(temperature=0,max_tokens=5)
#
#        response = llm.invoke(prompt)
#
#        decision = str(
#            response.content
#        ).strip().upper()
#
#        state["requires_research"] = (
#            decision == "RESEARCH"
#        )
#
#        return state
#
#    except Exception:
#        state["requires_research"] = False
#        return state
#
#
def research_decision_agent(state: AgentState):

    try:
        query = state.get("user_query")

        prompt = f"""
{GLOBAL_GUARDRAILS}

{RESEARCH_DECISION_PROMPT}

User Query:
{query}

Return exactly one word:
RESEARCH
or
NO_RESEARCH
"""

        llm = gemini_llm_client(
            model=GEMINI_MODEL,
            temperature=0,
            max_tokens=20
        )

        response = LLMService.invoke(
            llm=llm,
            prompt=prompt,
            state=state,
            agent="research_decision_agent",
            operation="research_decision",
        )

        raw_response = response.content

        decision = str(raw_response).strip().upper()

        print("\n========== RESEARCH DECISION ==========")
        print("RAW RESPONSE:", repr(raw_response))
        print("PARSED DECISION:", repr(decision))
        print("========================================\n")

        if decision not in {"RESEARCH", "NO_RESEARCH"}:
            raise ValueError(
                f"Invalid research decision: {decision!r}"
            )

        state["requires_research"] = (
            decision == "RESEARCH"
        )

        return state

    except Exception as e:

        print("\n========== RESEARCH DECISION ERROR ==========")
        print(repr(e))
        print("==============================================\n")

        # Safer default for your research agent:
        state["requires_research"] = True

        return state