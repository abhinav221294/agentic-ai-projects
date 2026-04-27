from utils.state import AgentState
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent
import re
import time

# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
def _set(state, start, answer, agent, confidence, decision_source, answer_source, trace_type, extra=None):
    state["answer"] = answer
    state["agent"] = agent
    state["confidence"] = confidence
    state["decision_source"] = decision_source
    state["answer_source"] = answer_source
    state["execution_time"] = round(time.time() - start, 2)

    trace_obj = {
        "step": "advisor",
        "type": trace_type
    }

    if extra:
        trace_obj.update(extra)

    state.setdefault("trace", []).append(trace_obj)

    return state


def advisor_agent(state: AgentState) -> AgentState:
    start = time.time()

    profile = state.get("profile") or {}
    memory = state.get("memory", [])

    last_msg = memory[-1] if memory else {}
    raw_query = last_msg.get("user", state.get("query", "")).strip()
    query = re.sub(r"[^\w\s]", " ", raw_query).lower().strip()

    state.setdefault("tools_used", [])
    state.setdefault("trace", [])

    # -------------------------
    # RETURNS SIGNAL (FIX)
    # -------------------------
    if "returns" in query:
        is_decision = True

    # -------------------------
    # INTENT DETECTION (moved early)
    # -------------------------
    is_decision = any(p in query for p in [
        "should", "invest", "what to do", "worth",
        "buy", "sell", "start", "choose"
    ])
    
    # -------------------------
    # PROFILE EXTRACTION
    # -------------------------
    age_match = re.search(r"\b([1-9][0-9])\b", query)
    if age_match:
        profile["age"] = age_match.group(1)

    if "low risk" in query:
        profile["risk"] = "low"
    elif "medium risk" in query:
        profile["risk"] = "medium"
    elif "high risk" in query:
        profile["risk"] = "high"

    if "income" in query:
        profile["goal"] = "income"
    elif "growth" in query:
        profile["goal"] = "growth"

    if "sip" in query:
        profile["investment_type"] = "sip"
    elif "lump sum" in query:
        profile["investment_type"] = "lump sum"

    state["profile"] = profile

    print(f"[ADVISOR] Query: {raw_query}")
    print(f"[ADVISOR] Profile: {profile}")

    needs_market = any(w in query for w in ["price", "market"])
    needs_risk = any(w in query for w in ["risk", "safe"])
    needs_news = any(w in query for w in ["news", "latest"])

    # -------------------------
    # DIRECT RECOMMENDATION
    # -------------------------
    if is_decision and all([
        profile.get("risk"),
        profile.get("goal"),
        profile.get("investment_type")
    ]):
        allocation = "60% Equity\n25% Debt\n15% Gold"

        answer = f"""
Based on your profile:

Risk: {profile['risk']}
Goal: {profile['goal']}
Investment: {profile['investment_type'].upper()}

Recommended Allocation:
{allocation}
"""

        return _set(
            state, start,
            answer,
            "advisor_agent", 0.9, "rule", "advisor",
            "recommendation"
        )

    # -------------------------
    # TOOL ORCHESTRATION (FIXED)
    # -------------------------
    context = {}
    tools = state.setdefault("tools_used", [])

    try:
        if needs_market:
            market_state = market_agent(state.copy())
            ans = market_state.get("answer", "")
            if ans and "unable" not in ans.lower():
                context["market"] = ans
            if "market_agent" not in tools:
                tools.append("market_agent")

        if needs_risk:
            risk_state = risk_agent(state.copy())
            ans = risk_state.get("answer", "")
            if ans and "unable" not in ans.lower():
                context["risk"] = ans
            if "risk_agent" not in tools:
                tools.append("risk_agent")

        if needs_news:
            news_state = news_agent(state.copy())
            ans = news_state.get("answer", "")
            if ans and "unable" not in ans.lower():
                context["news"] = ans
            if "news_agent" not in tools:
                tools.append("news_agent")

        # Always include RAG
        rag_state = rag_agent(state.copy())
        ans = rag_state.get("answer", "")
        if ans and "unable" not in ans.lower():
            context["knowledge"] = ans
        if "rag_agent" not in tools:
            tools.append("rag_agent")

        combined_context = "\n\n".join([
            f"{k.upper()}:\n{v}" for k, v in context.items() if v
        ])

        answer = f"""
Query: {raw_query}

Insights:
{combined_context}

Advice:
Based on the above, consider your risk tolerance and long-term goals before investing.
"""

        return _set(
            state, start,
            answer,
            "advisor_agent", 0.85, "advisor_reasoning", "advisor",
            "orchestration",
            {"tools": tools}
        )

    except Exception as e:
        print(f"[ADVISOR ERROR] {e}")

        return _set(
            state, start,
            "Unable to process request.",
            "advisor_agent", 0.2, "error", "advisor",
            "error",
            {"error": str(e)}
        )