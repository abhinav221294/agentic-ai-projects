from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ROUTER_PROMPT
import re

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag"}


# ---------------------------------------------------
#OLD VERSION (Rule-based router returning new dict)
# ---------------------------------------------------
# This was your initial implementation.
# It directly returned a new dictionary with "route".
#
#  Issues:
# - Not aligned with AgentState structure
# - Breaks shared state flow
# - Harder to scale in multi-agent systems
#
#def router_agent(state: dict) -> dict:
#    query = state["query"].lower()
#
#    market_keywords = ["price", "stock", "market", "value"]
#    risk_keywords = ["risk", "volatility", "loss", "danger"]
#    advisor_keywords = ["invest", "investment", "portfolio", "buy", "sell"]
#
#    if any(word in query for word in market_keywords):
#        return {"route": "market"}
#    
#    elif any(word in query for word in risk_keywords):
#        return {"route": "risk"}
#    
#    elif any(word in query for word in advisor_keywords):
#        return {"route": "advisor"}
#    
#    else:
#        return {"route": "rag"}
#    


# ---------------------------------------------------
# NEW VERSION (State-based router - Recommended)
# ---------------------------------------------------
# This version uses AgentState and modifies it directly.
# This is the correct approach for:
# - Multi-agent systems
# - LangGraph workflows
# - Scalable architecture

def router_agent(state: AgentState) -> AgentState:
    """
    Router Agent

    Purpose:
    - Classifies user query into a category
    - Updates the shared state with routing decision

    Categories:
    - market   → stock prices, market data
    - risk     → risk analysis, volatility
    - advisor  → investment advice
    - rag      → fallback (general queries)

    Args:
        state (AgentState):
            {
                "query": str,
                "category": str,
                "answer": str
            }

    Returns:
        AgentState (updated with category)
    """

    # ---------------------------------------------------
    # Step 1: Normalize query
    # ---------------------------------------------------
    # Convert query to lowercase for case-insensitive matching
    
    raw_query = state["query"]
    query = raw_query.lower()

    memory = state.get("memory", [])

    #context_text = " ".join([m.get("user", "") for m in memory[-3:]]).lower()

    #full_query = context_text + " " + query
    full_query = query

    if state.get("clarification_needed"):
        state["category"] = "advisor"
        return state

    # ---------------------------------------------------
    # Step 2: Define keyword groups for each category
    # ---------------------------------------------------
    # These keywords act as simple intent classifiers

    
    # ---------------------------------------------------
    # Step 3: Routing logic
    # ---------------------------------------------------
    # Check if any keyword exists in query using:
    # any() → returns True if at least one match is found

    # # ---------------------------------------------------
    # Step 3: Routing logic (FIXED)
    # ---------------------------------------------------
    

    # 🔹 Definition queries → RAG
    if full_query.startswith("what is") or full_query.startswith("define"):
        state["category"] = "rag"

    if "news" in full_query:
        state["category"] = "news"
        return state
    
    try:
        llm = get_llm()
        prompt = f"""{ROUTER_PROMPT}

You are a strict intent classifier.

IMPORTANT:
- If the query asks for advice, recommendation, or decision → advisor
- If the query asks for price/data only → market
- If asking about safety → risk
- If asking news → news
- Else → rag

Query:
{full_query}

Return ONLY one word:
market / risk / advisor / news / rag
"""
        
        reponse = llm.invoke(prompt)
        raw_output = reponse.context.strip().lower()
        category = re.sub(r"[^a-z]","", raw_output)

        if category in VALID_CATEGORIES:
            state["category"] = category
            return state
        

    except:
        pass
    # -------------------------
    # 🔒 Guardrail 5: Rule-based fallback (SAFE)
    # -------------------------
    market_keywords = ["price", "stock", "market", "value"]
    risk_keywords = ["risk","risky", "volatility", "loss", "danger","safe"]
    advisor_keywords = ["invest", "investment", "portfolio", "buy", "sell"]
    news_keywords = ["news", "headlines", "updates"]

    if any(word in full_query for word in advisor_keywords):
        state["category"] = "advisor"

    elif any(word in full_query for word in market_keywords):
        state["category"] = "market"

    elif any(word in full_query for word in risk_keywords):
        state["category"] = "risk"

    elif any(word in full_query for word in news_keywords):
        state["category"] = "news"

    else:
        state["category"] = "rag"

    return state