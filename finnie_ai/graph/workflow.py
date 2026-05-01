from langgraph.graph import StateGraph, END

from utils.state import AgentState
from agents.rag_agent import rag_agent
from agents.router_agent import router_agent
from agents.risk_agent import risk_agent
from agents.advisor_agent import advisor_agent
from agents.market_agent import market_agent
from agents.news_agent import news_agent
from utils.llm import get_llm
import uuid
import time


# -------------------------
# FALLBACK AGENT
# -------------------------
def fallback_agent(state: AgentState) -> AgentState:
    
    start_time = time.time()
    query = state.get("query", "").lower()

    llm = get_llm(temperature=0.2)

    try:
        response = llm.invoke(f"""
User asked: "{query}"

You're a finance-focused assistant having a casual chat.

Respond in 2–3 lines:
- Mention the topic briefly
- Say you focus on finance
- Mention your scope casually

Tone: casual, not formal
""")

        answer = response.content.strip() if response and response.content else \
            "I usually focus on finance—things like investing and markets."

    except Exception as e:
        answer = "I usually focus on finance—things like investing and markets."

    state["answer"] = answer
    state["agent"] = "fallback_agent"
    state["execution_time"] = round(time.time() - start_time, 3)
    return state


# -------------------------
# BUILD WORKFLOW
# -------------------------
def __build_workflow():

    workflow = StateGraph(AgentState)

    # -------------------------
    # NODES
    # -------------------------
    workflow.add_node("router_agent", router_agent)
    workflow.add_node("rag_agent", rag_agent)
    workflow.add_node("market_agent", market_agent)
    workflow.add_node("risk_agent", risk_agent)
    workflow.add_node("advisor_agent", advisor_agent)
    workflow.add_node("news_agent", news_agent)
    workflow.add_node("fallback_agent", fallback_agent)

    # -------------------------
    # ENTRY
    # -------------------------
    workflow.set_entry_point("router_agent")

    # -------------------------
    # ROUTING LOGIC (FINAL)
    # -------------------------
    def __route_decision(state: AgentState):
        decision = "fallback_agent"
        category = state.get("category", "none")
        complexity = state.get("complexity", "simple")
        confidence = state.get("confidence", 1.0)
        query = state.get("query", "")
        if not isinstance(category, str):
            decision = "fallback_agent"


        # 🔍 DEBUG LOG
        # -------------------------
        # 🔥 PRIORITY ROUTING
        # -------------------------

        # Always advisor if explicitly classified
        elif category == "advisor":
            decision = "advisor_agent"

        # Low confidence OR complex → advisor
        elif  complexity == "complex" or confidence < 0.6:
            decision = "advisor_agent"

        # -------------------------
        # ⚡ SIMPLE DIRECT ROUTING
        # -------------------------
        elif  category == "market":
            decision = "market_agent"

        elif  category == "risk":
            decision = "risk_agent"

        elif  category == "news":
            decision = "news_agent"

        elif  category == "rag":
            decision = "rag_agent"

        state.setdefault("trace", []).append({
         "agent": "router_agent",
        "action": "route",
        "decision": decision})

        return decision


    # -------------------------
    # CONDITIONAL EDGES
    # -------------------------
    workflow.add_conditional_edges(
        "router_agent",
        __route_decision
    )

    # -------------------------
    # TERMINATION
    # -------------------------
    workflow.add_edge("rag_agent", END)
    workflow.add_edge("market_agent", END)
    workflow.add_edge("risk_agent", END)
    workflow.add_edge("advisor_agent", END)
    workflow.add_edge("news_agent", END)
    workflow.add_edge("fallback_agent", END)

    return workflow.compile(checkpointer=None)


# -------------------------
# APP INSTANCE
# -------------------------
app = __build_workflow()


# -------------------------
# RUN FUNCTION
# -------------------------
def run_workflow(state: dict):
    state.setdefault("trace", [])
    # Ensure profile exists
    if "profile" not in state:
        state["profile"] = {
            "age": None,
            "risk": None,
            "goal": None,
            "investment_type": None
        }

    result = app.invoke(
        state,
        config={
            "recursion_limit": 10,
            "configurable": {
                "thread_id": str(uuid.uuid4())
            }
        }
    )

    if not result:
        return {"answer": "Something went wrong.", "agent": "system",
        "trace": state.get("trace", [])}

    return {
    "answer": result.get("answer"),
    "agent": result.get("agent"),
    "trace": result.get("trace", []),
    "tools_used": result.get("tools_used", []),
    "execution_time": state.get("execution_time"),
    "confidence": result.get("confidence"),
    "profile": result.get("profile", {}),   # 🔥 THIS FIXES EVERYTHING
    "stage": result.get("stage")
    }