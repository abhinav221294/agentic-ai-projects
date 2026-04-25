from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ROUTER_PROMPT
import re
from utils.stock_mapper import normalize_stock

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}


def router_agent(state: AgentState) -> AgentState:

    query = state["query"]
    query_lower = query.lower()
    memory = state.get("memory", [])
    symbol = normalize_stock(query)

    

    # FOLLOW-UP (HIGHEST PRIORITY)
    FOLLOW_UP_PHRASES = [
    "what do you think",
    "based on",
    "is it good",
    "should i",
    "what about",
    "how about",
    "tell me more"
    ]

    is_follow_up = (
        len(memory) > 0 and
        (
        any(p in query_lower for p in FOLLOW_UP_PHRASES)
        or len(query_lower.split()) <= 7   # short query heuristic
        ))
        
    # Only treat as follow-up if it's vague AND short
    is_vague = not any(w in query_lower for w in [
        "price", "stock", "share", "risk", "invest", "buy", "sell"
    ]) and symbol is None

    FINANCE_KEYWORDS = [
    "stock", "market", "price", "nifty", "sensex",
    "investment", "invest", "portfolio", "sip",
    "mutual fund", "etf", "bond", "equity", "debt",
    "risk", "volatility", "return", "dividend",
    "crypto", "trading"]

    # FOLLOW-UP (only if no strong signal)
    if is_follow_up:
        state["category"] = "advisor"
        return state


    # 🔹 Allow definition-type queries (handled later)
    is_definition = query_lower.startswith(("what is", "define", "explain"))

    # 🔴 HARD STOP (only if clearly non-finance AND not follow-up)


    
    if not any(word in query_lower for word in FINANCE_KEYWORDS) and not is_follow_up and not symbol:
        print("[Router] Non-finance query detected → stopping")
        state["category"] = "none"
        return state

    # ---------------------------------------------------
    # 🔹 RULE-BASED ROUTING (FAST PATH)
    # ---------------------------------------------------

       # -------------------------
    # MARKET
    # -------------------------

    PRICE_KEYWORDS = ["price", "quote", "current", "latest", "now"]

    #if any(word in query_lower for word in ["price", "stock", "nifty", "sensex", "share"]):
    if symbol and (
    any(word in query_lower for word in PRICE_KEYWORDS)
    or len(query_lower.split()) <= 3
    ):
        state["category"] = "market"
        return state
    
    # -------------------------
    # RAG (definitions FIRST)
    # -------------------------
    if query_lower.startswith(("what is", "define", "explain")):
        if any(word in query_lower for word in FINANCE_KEYWORDS):
            state["category"] = "rag"
        else:
            state["category"] = "none"
        return state
    
    # -------------------------
    # STOCK + RISK → ADVISOR (orchestration)
    # -------------------------
    if symbol and any(word in query_lower for word in ["risk", "risky"]):
        state["category"] = "advisor"
        return state
    
    # -------------------------
    # RISK (only pure risk queries)
    # -------------------------
    # -------------------------
    # RISK (higher priority)
    # -------------------------
    if any(word in query_lower for word in ["risk", "risky", "volatility", "loss", "danger", "safe"]):

        # ✅ If explicitly asking "what should I do" → advisor
        if any(word in query_lower for word in [
        "suggest", "plan", "allocate", "where", "portfolio"
        ]):
            pass  # advisor will handle

        else:
            state["category"] = "risk"
            return state

    if any(word in query_lower for word in [
        "invest", "investment", "buy", "sell", "portfolio",
        "should i", "goal", "lump", "sip"
    ]):
        state["category"] = "advisor"
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