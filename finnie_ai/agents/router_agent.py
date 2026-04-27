from utils.state import AgentState
from utils.llm import get_llm
import re
from dotenv import load_dotenv
load_dotenv()

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}


# -------------------------
# CENTRAL SETTER
# -------------------------
def _set(state, category, confidence, source, reason=None):
    state["category"] = category
    state["confidence"] = confidence
    state["decision_source"] = source

    state.setdefault("trace", []).append({
        "step": "router",
        "method": source,
        "category": category,
        "confidence": confidence,
        "reason": reason
    })

    return state


def router_agent(state: AgentState) -> AgentState:
    query = state["query"]
    memory = state.get("memory", [])

    q = re.sub(r"[^\w\s]", "", query.lower().strip())

    RAG_TOPICS = [
        "sip", "mutual", "stocks", "stock",
        "bonds", "bond", "inflation",
        "diversification", "risk", "crypto", "bitcoin"
    ]

    # -------------------------
    # SHORT QUERY HANDLING
    # -------------------------
    if len(q.split()) == 1:
        if any(topic in q for topic in RAG_TOPICS):
            return _set(state, "rag", 0.85, "rule", "single_word_topic")
        else:
            return _set(state, "none", 0.85, "rule", "single_word_unknown")

    # -------------------------
    # STRONG RULES
    # -------------------------
    if any(phrase in q for phrase in [
        "safe or not", "is it safe", "is it risky", "risky or not"
    ]):
        return _set(state, "risk", 0.95, "rule", "explicit_risk_check")

    if any(phrase in q for phrase in [
        "how to invest", "how do i invest", "where to invest",
        "should i invest", "how to start", "how to begin"
    ]):
        return _set(state, "advisor", 0.95, "rule", "explicit_decision")

    # -------------------------
    # LLM CLASSIFICATION
    # -------------------------
    try:
        llm = get_llm(temperature=0)

        prompt = f"""
You are a financial query classifier.

Your job is to understand INTENT (not keywords).

---

Classify the query into EXACTLY ONE:
- advisor (user asking what to do / decision)
- risk (asking about safety or risk only)
- market (asking price/value of asset)
- news (latest updates/news)
- rag (definition/explanation only)
- none (non-finance)

---

IMPORTANT RULES:

1. If user asks ANY decision → advisor wins
2. If query has mixed intent → advisor wins
3. If ONLY asking definition → rag
4. If ONLY asking risk → risk
5. If ONLY asking price → market
6. If ONLY asking news → news
7. If unrelated to finance → none
8. If vague but implies choice (e.g. "safe option?") → advisor

Also consider previous context:
{memory}

---

Return STRICT JSON:
{{
  "category": "<advisor|risk|market|news|rag|none>",
  "confidence": 0.0 to 1.0,
  "reason": "short explanation"
}}

Query: {query}
"""

        res = llm.invoke(prompt)
        text = res.content.strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            data = eval(match.group())

            category = data.get("category")
            confidence = float(data.get("confidence", 0.7))
            reason = data.get("reason", "")

            if category in VALID_CATEGORIES:
                return _set(state, category, confidence, "llm", reason)

    except Exception as e:
        print(f"[Router Error] {e}")

    # -------------------------
    # FALLBACK (FIXED)
    # -------------------------
    return _set(state, "advisor", 0.5, "fallback", "llm_failed")