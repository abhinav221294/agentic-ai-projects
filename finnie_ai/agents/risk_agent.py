from utils.state import AgentState


def risk_agent(state: AgentState) -> AgentState:
    """
    Risk Agent

    Purpose:
    - Classify investment risk based on query
    - Provide clear explanation
    - Add advisory tip for better UX
    - Update state with answer + agent
    """

    # ---------------------------------------------------
    # Step 1: Normalize query
    # ---------------------------------------------------
    raw_query = state["query"]
    query = raw_query.lower()

    # ---------------------------------------------------
    # Step 2: Define keyword groups
    # ---------------------------------------------------
    high_risk_keywords = ["crypto", "bitcoin", "trading", "options", "futures"]
    medium_risk_keywords = ["stock", "equity", "shares"]
    low_risk_keywords = ["fd", "fixed deposit", "bond", "government", "ppf"]
     
    # ---------------------------------------------------
    # Step 3: Default values
    # ---------------------------------------------------
    risk_level = "Medium ⚖️"
    explanation = ""

    # ---------------------------------------------------
    # Step 4: Risk classification
    # ---------------------------------------------------
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
    # Step 5: Add advisory tip (UX improvement)
    # ---------------------------------------------------
    tip = "Tip: Consider your investment horizon and financial goals."

    # ---------------------------------------------------
    # Step 6: Build response
    # ---------------------------------------------------
    response = (
        f"Risk Level: {risk_level}\n"
        f"{explanation}\n\n"
        f"{tip}"
    )

    # ---------------------------------------------------
    # Step 7: Update state
    # ---------------------------------------------------
    state["answer"] = response
    state["agent"] = "risk_agent" 
    state["confidence"] = "HIGH"  

    return state