from utils.state import AgentState
import re
import time


# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
def _set(state, start, answer, confidence, extra=None):
    state["answer"] = answer
    state["agent"] = "risk_agent"
    state["confidence"] = confidence
    state["decision_source"] = "rule"
    state["answer_source"] = "risk_logic"
    state["execution_time"] = round(time.time() - start, 2)

    if extra:
        state.update(extra)

    return state


def risk_agent(state: AgentState) -> AgentState:
    start = time.time()

    state.setdefault("trace", []).append("risk_agent")

    # -------------------------
    # Step 1: Normalize query
    # -------------------------
    raw_query = state["query"]
    query = re.sub(r"[^\w\s]", "", raw_query.lower().strip())

    memory = state.get("memory", [])

    FOLLOW_UP_WORDS = [
        "why", "how", "explain", "reason",
        "detail", "details", "clarify",
        "elaborate", "more", "expand"
    ]

    FOLLOW_UP_PHRASES = [
        "tell me more",
        "explain more",
        "can you explain",
        "why is that"
    ]

    words = query.split()

    is_followup_signal = (
        any(w in words for w in FOLLOW_UP_WORDS) or
        any(p in query for p in FOLLOW_UP_PHRASES)
    )

    is_follow_up = memory and is_followup_signal

    state["query_type"] = "follow_up" if is_follow_up else "fresh"

    # -------------------------
    # Step 2: Skip invalid short inputs
    # -------------------------
    if memory and len(words) <= 2:
        if not is_followup_signal:
            return _set(
                state, start,
                "Please ask a clear question about risk.",
                0.5
            )

    # -------------------------
    # Step 3: Get last answer
    # -------------------------
    last_answer = next(
        (m.get("assistant", "") for m in reversed(memory) if m.get("assistant")),
        ""
    )
    last_answer_lower = last_answer.lower()

    # -------------------------
    # Step 4: Handle follow-up
    # -------------------------
    if is_follow_up and "risk level" in last_answer_lower:

        if "high" in last_answer_lower:
            risk_level = "High ⚠️"
            explanation = (
                "Cryptocurrency is risky due to high volatility, rapid price swings, "
                "regulatory uncertainty, and strong influence of market sentiment."
            )

        elif "low" in last_answer_lower:
            risk_level = "Low ✅"
            explanation = (
                "These investments are considered low risk because they offer stable "
                "and predictable returns with minimal market fluctuation."
            )

        else:
            risk_level = "Medium ⚖️"
            explanation = (
                "These investments carry moderate risk due to market fluctuations, "
                "but also offer balanced return potential."
            )

        tip = "Tip: Consider your investment horizon and financial goals."

        return _set(
            state, start,
            f"Risk Level: {risk_level}\n{explanation}\n\n{tip}",
            0.8
        )

    # -------------------------
    # Step 5: Risk classification
    # -------------------------
    high_risk_keywords = ["crypto", "bitcoin", "trading", "options", "futures"]
    medium_risk_keywords = ["stock", "equity", "shares"]
    low_risk_keywords = ["fd", "fixed deposit", "bond", "government", "ppf"]

    risk_level = "Medium ⚖️"

    if any(word in words for word in high_risk_keywords):
        risk_level = "High ⚠️"
        explanation = (
            "These investments are highly volatile and can lead to "
            "significant gains or losses in a short time."
        )

    elif any(word in words for word in low_risk_keywords):
        risk_level = "Low ✅"
        explanation = (
            "These are relatively stable investments with predictable "
            "returns but lower growth potential."
        )

    elif any(word in words for word in medium_risk_keywords):
        explanation = (
            "These investments offer balanced risk and return, but "
            "market fluctuations can still impact performance."
            "Investment risk depends on asset type and market factors."
        )

    else:
        explanation = (
            "Investment risk depends on asset type, market conditions, "
            "and your investment horizon."
        )

    # -------------------------
    # Step 6: Final response
    # -------------------------
    tip = "Tip: Consider your investment horizon and financial goals."

    return _set(
        state, start,
        f"Risk Level: {risk_level}\n{explanation}\n\n{tip}",
        0.8
    )