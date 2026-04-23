from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ROUTER_PROMPT
import re

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}


def router_agent(state: AgentState) -> AgentState:

    query = state["query"]
    query_lower = query.lower()
    memory = state.get("memory", [])

    FINANCE_KEYWORDS = [
    "stock", "market", "price", "nifty", "sensex",
    "investment", "invest", "portfolio", "sip",
    "mutual fund", "etf", "bond", "equity", "debt",
    "risk", "volatility", "return", "dividend",
    "crypto", "trading"]

    is_follow_up = len(memory) > 0 and any(
    query_lower in m.get("user", "").lower()
    for m in memory[-2:]
    )

    # 🔹 Allow definition-type queries (handled later)
    is_definition = query_lower.startswith(("what is", "define", "explain"))

    # 🔴 HARD STOP (only if clearly non-finance AND not follow-up)
    if not any(word in query_lower for word in FINANCE_KEYWORDS) and not is_follow_up and not is_definition:
        print("[Router] Non-finance query detected → stopping")
        state["category"] = "none"
        return state

    # ---------------------------------------------------
    # 🔹 RULE-BASED ROUTING (FAST PATH)
    # ---------------------------------------------------

    # Market
    if any(word in query_lower for word in ["price", "stock", "nifty", "sensex", "share"]):
        state["category"] = "market"
        return state

    # Risk
    if any(word in query_lower for word in ["risk", "volatility", "loss", "danger", "safe"]):
        state["category"] = "risk"
        return state

    # Advisor
    if any(word in query_lower for word in ["invest", "investment", "buy", "sell", "portfolio", "should i"]):
        state["category"] = "advisor"
        return state

    # News
    if any(word in query_lower for word in ["news", "latest", "update", "headline"]):
        state["category"] = "news"
        return state

    # RAG (definitions)
    if query_lower.startswith(("what is", "define", "explain")):
        if any(word in query_lower for word in FINANCE_KEYWORDS):
            state["category"] = "rag"
        else:
            state["category"] = "none"
        return state
    

    # ---------------------------------------------------
    # 🔹 BUILD CONTEXT (for LLM)
    # ---------------------------------------------------

    conversation = ""
    for m in memory[-4:]:
        conversation += f"User: {m.get('user', '')}\nAssistant: {m.get('assistant', '')}\n"

    full_input = f"""Conversation:
{conversation}

User Query:
{query}

IMPORTANT:
- If the query is a follow-up (e.g., "what should I do with it", "explain more"):
  → Continue naturally from previous conversation
  → Do NOT restart explanation
  → Do NOT repeat full analysis
  → Give a direct, simple answer

- Only give detailed structured responses when explicitly needed
"""

    # ---------------------------------------------------
    # 🔹 LLM ROUTING (FALLBACK)
    # ---------------------------------------------------

    try:
        llm = get_llm()

        response = llm.invoke(f"""{ROUTER_PROMPT}

{full_input}
""")

        raw_output = response.content.strip().lower()

        # Clean + tokenize
        clean_output = re.sub(r"[^a-z]", " ", raw_output)
        tokens = clean_output.split()

        # Priority-based deterministic routing
        PRIORITY = ["risk", "advisor", "market", "news", "rag", "none"]

        matched_category = None
        for category in PRIORITY:
            if category in tokens:
                matched_category = category
                break

        if matched_category:
            state["category"] = matched_category
            return state
        else:
            print(f"[Router Warning] Unexpected output: {raw_output}")
            state["category"] = "none"
            return state

    except Exception as e:
        print(f"[Router Error] {e}")

    # ---------------------------------------------------
    # 🔹 SAFE FALLBACK
    # ---------------------------------------------------
    state["category"] = "none"
    return state