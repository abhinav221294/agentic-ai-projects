from utils.state import AgentState
from utils.llm import get_llm
import re

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}
from dotenv import load_dotenv
load_dotenv()

def router_agent(state: AgentState) -> AgentState:

    query = state["query"]
    memory = state.get("memory", [])
    q = query.lower()

    # -------------------------
    # 1. FOLLOW-UP (keep this)
    # -------------------------
    if memory and len(q.split()) <= 5:
        state["category"] = "advisor"
        return state

    # -------------------------
    # 2. STRONG SIGNALS ONLY
    # -------------------------
    if "price" in q:
        state["category"] = "market"
        return state

    if "news" in q or "latest" in q:
        state["category"] = "news"
        return state

    # -------------------------
    # 3. LLM DOES THE WORK
    # -------------------------
    try:
        llm = get_llm(temperature=0.1)

        prompt = f"""
You are a financial intent classifier.

Classify into ONE:
market, risk, advisor, news, rag, none

IMPORTANT RULES:

1. If query contains BOTH:
   - concept (what is / explain)
   AND
   - action/advice (invest / good / suggest / plan)
   → ALWAYS return: advisor

2. If query asks about:
   - returns, investment, plan, portfolio
   → advisor

3. If query is short but finance-related:
   - "crypto", "sip", "returns"
   → rag (unless asking advice)

4. If asking safety:
   - "safe", "risky"
   → risk
   If query asks:
- "safe or not", "risky or not"
→ always return: risk

Only return advisor if:
- explicitly asking what to do (invest, buy, suggest, plan)

EXAMPLE:
"crypto safe or not?" → risk

5. Definitions only:
   → rag

Examples:

"What is SIP" → rag
"What is SIP and how to invest" → advisor
"returns?" → advisor
"SIP investment plan" → advisor
"crypto" → rag
"bond returns safe?" → advisor
"risk?" → risk

Return ONLY one word.

Query: {query}
"""

        res = llm.invoke(prompt)
        out = re.sub(r"[^a-z]", "", res.content.lower())

        if out in VALID_CATEGORIES:
            state["category"] = out
            return state

    except Exception as e:
        print(f"[Router Error] {e}")

    # -------------------------
    # 4. FALLBACK
    # -------------------------
    state["category"] = "advisor"
    return state