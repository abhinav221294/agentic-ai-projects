from utils.state import AgentState


def risk_agent(state: AgentState) -> AgentState:
    """
    Risk Agent

    Purpose:
    - Classify investment risk based on query
    - Handle follow-up questions intelligently
    - Provide clear explanation
    - Add advisory tip
    """

    # ---------------------------------------------------
    # Step 1: Normalize query
    # ---------------------------------------------------
    raw_query = state["query"]
    query = raw_query.lower()

    memory = state.get("memory", [])

    # ---------------------------------------------------
    # Step 2: Skip invalid short inputs
    # ---------------------------------------------------
    if memory:
        if "?" not in raw_query and not any(q in query for q in ["what", "how", "explain", "why"]):
            state["skip"] = True
            return state

    # ---------------------------------------------------
    # Step 3: Follow-up detection
    # ---------------------------------------------------
    FOLLOW_UP_WORDS = ["why", "how", "explain", "reason"]

    is_follow_up = any(w in query for w in FOLLOW_UP_WORDS)

    last_answer = next(
        (m.get("assistant", "") for m in reversed(memory) if m.get("assistant")),
        ""
    )

    # ---------------------------------------------------
    # Step 4: Handle follow-up (IMPORTANT)
    # ---------------------------------------------------
    if is_follow_up and "risk level" in last_answer.lower():

        if "high" in last_answer.lower():
            risk_level = "High ⚠️"
            explanation = (
                "Cryptocurrency is risky due to high volatility, rapid price swings, "
                "regulatory uncertainty, and strong influence of market sentiment."
            )

        elif "low" in last_answer.lower():
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

        state["answer"] = f"Risk Level: {risk_level}\n{explanation}\n\n{tip}"
        state["agent"] = "risk_agent"
        state["confidence"] = "HIGH"

        return state   # 🔥 EARLY RETURN (critical)

    # ---------------------------------------------------
    # Step 5: Risk classification
    # ---------------------------------------------------
    high_risk_keywords = ["crypto", "bitcoin", "trading", "options", "futures"]
    medium_risk_keywords = ["stock", "equity", "shares"]
    low_risk_keywords = ["fd", "fixed deposit", "bond", "government", "ppf"]

    risk_level = "Medium ⚖️"
    explanation = ""

    if any(word in query for word in high_risk_keywords):
        risk_level = "High ⚠️"
        explanation = (
            "These investments are highly volatile and can lead to "
            "significant gains or losses in a short time."
        )

    elif any(word in query for word in low_risk_keywords):
        risk_level = "Low ✅"
        explanation = (
            "These are relatively stable investments with predictable "
            "returns but lower growth potential."
        )

    elif any(word in query for word in medium_risk_keywords):
        risk_level = "Medium ⚖️"
        explanation = (
            "These investments offer balanced risk and return, but "
            "market fluctuations can still impact performance."
        )

    else:
        explanation = (
            "Investment risk depends on market conditions, asset type, "
            "and time horizon."
        )

    # ---------------------------------------------------
    # Step 6: Build response
    # ---------------------------------------------------
    tip = "Tip: Consider your investment horizon and financial goals."

    state["answer"] = f"Risk Level: {risk_level}\n{explanation}\n\n{tip}"
    state["agent"] = "risk_agent"
    state["confidence"] = "HIGH"

    return state