from langgraph.graph import StateGraph, END

from utils.state import AgentState
from agents.rag_agent import rag_agent
from agents.router_agent import router_agent
from agents.risk_agent import risk_agent
from agents.advisor_agent import advisor_agent
from agents.market_agent import market_agent
from agents.news_agent import news_agent

def __build_workflow():
    """
    Builds and compiles a LangGraph workflow for a multi-agent system.

    Flow:
    1. Start with router_agent (entry point)
    2. Router decides category based on query
    3. Conditional routing sends state to appropriate agent
    4. Selected agent processes query and updates state
    5. Workflow terminates at END

    Returns:
        Compiled LangGraph workflow (ready to invoke)
    """

    # ---------------------------------------------------
    # Step 1: Initialize workflow with state schema
    # ---------------------------------------------------
    # AgentState defines structure of shared data:
    # {
    #   "query": str,
    #   "category": str,
    #   "answer": str
    # }
    workflow = StateGraph(AgentState)

    # ---------------------------------------------------
    # Step 2: Register all agents (nodes)
    # ---------------------------------------------------
    # Each node represents a function that:
    # - takes state as input
    # - modifies it
    # - returns updated state

    workflow.add_node("router_agent", router_agent)     # decides route
    workflow.add_node("rag_agent", rag_agent)           # general Q&A
    workflow.add_node("market_agent", market_agent)     # stock/price queries
    workflow.add_node("risk_agent", risk_agent)         # risk-related queries
    workflow.add_node("advisor_agent", advisor_agent)   # investment advice
    workflow.add_node("news_agent", news_agent) 
    # ---------------------------------------------------
    # Step 3: Define entry point
    # ---------------------------------------------------
    # Workflow always starts with router_agent
    workflow.set_entry_point("router_agent")

    # ---------------------------------------------------
    # Step 4: Define valid categories
    # ---------------------------------------------------
    # This acts as a safeguard to avoid invalid routing
    __VALID_CATEGORIES = {"rag", "market", "risk", "advisor","news"}

    # ---------------------------------------------------
    # Step 5: Routing decision function
    # ---------------------------------------------------
    # This function reads state["category"] (set by router_agent)
    # and determines which node to execute next

    def __route_decision(state: AgentState):
        # Get category from state (default to "rag" if missing)
        category = state.get("category", "rag")

        # Return category only if valid, else fallback to "rag"
        return category if category in __VALID_CATEGORIES else "rag"
    
    # ---------------------------------------------------
    # Step 6: Add conditional edges
    # ---------------------------------------------------
    # Based on output of route_decision:
    # - "rag"     → rag_agent
    # - "market"  → market_agent
    # - "risk"    → risk_agent
    # - "advisor" → advisor_agent

    workflow.add_conditional_edges(
        "router_agent",       # source node
        __route_decision,       # decision function
        {
            "rag": "rag_agent",
            "market": "market_agent",
            "risk": "risk_agent",
            "advisor": "advisor_agent",
            "news": "news_agent"
        }
    )

    # ---------------------------------------------------
    # Step 7: Define termination (END)
    # ---------------------------------------------------
    # After each agent finishes execution, workflow ends

    workflow.add_edge("rag_agent", END)
    workflow.add_edge("market_agent", END)
    workflow.add_edge("risk_agent", END)
    workflow.add_edge("advisor_agent", END)
    workflow.add_edge("news_agent", END)

    # ---------------------------------------------------
    # Step 8: Compile workflow
    # ---------------------------------------------------
    # Converts graph definition into executable object

    return workflow.compile()

app = __build_workflow()

def run_workflow(state: dict):
    return app.invoke(state)