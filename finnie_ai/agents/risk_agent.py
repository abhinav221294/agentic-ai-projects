# -------------------------
# IMPORTS
# -------------------------
# Agent state schema for passing data between agents
from utils.state import AgentState

# Used for text cleaning and pattern matching
import re

# Used for tracking execution time
import time
from utils.state_utils import set_state
# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------

def get_risk_tip(risk_level):

    if "high" in risk_level :
        return "Tip: High-risk investments can be very volatile. Invest only what you can afford to lose and focus on long-term strategy."

    if  "medium" in risk_level:
        return "Tip: Medium-risk investments balance growth and stability. Diversify your portfolio to manage risk effectively."

    if  "low" in risk_level:
        return "Tip: Low-risk investments provide stability but may offer lower returns. Consider inflation when planning long-term goals."

    return "Tip: Always align investments with your financial goals and risk tolerance."

def risk_agent(state: AgentState) -> AgentState:
    """
    Main risk analysis agent.

    Responsibilities:
    - Detect follow-up queries
    - Classify investment risk level
    - Provide explanation + guidance
    """

    # Start execution timer
    start = time.time()

    # Add trace for debugging / observability
    state.setdefault("trace", []).append({
        "agent": "risk_agent",
        "action": "analyze_risk"
    })

    # -------------------------
    # Step 1: Normalize query
    # -------------------------
    # Get raw query
    raw_query = state["query"]

    # Clean query: lowercase + remove punctuation
    query = re.sub(r"[^\w\s]", "", raw_query.lower().strip())

    # Retrieve conversation memory
    memory = state.get("memory", [])

    # -------------------------
    # FOLLOW-UP DETECTION (RULE-BASED)
    # -------------------------
    # Words indicating follow-up intent
    FOLLOW_UP_WORDS = [
        "why", "how", "explain", "reason",
        "detail", "details", "clarify",
        "elaborate", "more", "expand"
    ]

    # Phrases indicating follow-up
    FOLLOW_UP_PHRASES = [
        "tell me more",
        "explain more",
        "can you explain",
        "why is that"
    ]

    # Split query into words
    words = query.split()

    # Detect follow-up signals
    is_followup_signal = (
        any(w in words for w in FOLLOW_UP_WORDS) or
        any(p in query for p in FOLLOW_UP_PHRASES)
    )

    # Final follow-up condition
    is_follow_up = bool(memory) and is_followup_signal

    # Store query type in state
    state["query_type"] = "follow_up" if is_follow_up else "fresh"

    # -------------------------
    # Step 2: Skip invalid short inputs
    # -------------------------
    # If query is too short and not a follow-up → ask for clarification
    if memory and len(words) <= 2:
        if not is_followup_signal:
            return set_state(
            state,
            start,
            answer="Please ask a clear question about risk.",
            agent="risk_agent",
            confidence=0.5,
            decision_source="rule",
            answer_source="risk_logic",
            trace_action="clarify",
            )
    # -------------------------
    # Step 3: (Reserved for future logic)
    # -------------------------
    # Currently no logic here (placeholder)

    # -------------------------
    # Step 4: Handle follow-up queries
    # -------------------------
    if is_follow_up and state.get("risk_level"):
        # Get previous risk level
        prev_level = state.get("risk_level", "").lower()
        risk_level = ""
        
        # Provide deeper explanation based on previous classification
        if prev_level.startswith("high"):
            risk_level = "High ⚠️"
            explanation = (
            "These investments carry high risk due to significant price volatility, "
            "uncertain market conditions, and sensitivity to external factors such as "
            "economic changes, news, and investor sentiment. Returns can be high, "
            "but losses can also occur quickly."
            )

        elif prev_level.startswith("low"):
            risk_level = "Low ✅"
            explanation = (
                "These investments are considered low risk because they offer relatively stable "
                "and predictable returns. They are less affected by market fluctuations and are "
                "generally suitable for capital preservation and steady income generation."
            )

        else:
            risk_level = "Medium ⚖️"
            explanation = (
                "These investments carry moderate risk, balancing potential returns with "
                "exposure to market fluctuations. While they can provide growth, their value "
                "may vary depending on market conditions and economic factors."
            )

        # General financial tip
        tip = get_risk_tip(risk_level=risk_level.lower())

    
        return set_state(
        state,
        start,
        answer=f"Risk Level: {risk_level}\n{explanation}\n\n{tip}",
        agent="risk_agent",
        confidence=0.8,
        decision_source="rule",
        answer_source="risk_logic",
        trace_action="followup",
        extra={
        "risk_level": risk_level,
        "risk_explanation": explanation
        }
        )
    # -------------------------
    # Step 5: Risk classification
    # -------------------------
    # Define keyword buckets for risk levels
    high_risk_keywords = ["crypto", "bitcoin", "trading", "options", "futures"]
    medium_risk_keywords = ["stock", "equity", "shares"]
    low_risk_keywords = ["fd", "fixed deposit", "bond", "government", "ppf"]

    # Default risk level
    risk_level = "Medium ⚖️"

    # High risk detection
    if any(word in words for word in high_risk_keywords):
        risk_level = "High ⚠️"
        explanation = (
            "These investments are highly volatile and can lead to "
            "significant gains or losses in a short time."
        )

    # Low risk detection
    elif any(word in words for word in low_risk_keywords):
        risk_level = "Low ✅"
        explanation = (
            "These are relatively stable investments with predictable "
            "returns but lower growth potential."
        )

    # Medium risk detection
    elif any(word in words for word in medium_risk_keywords):
        explanation = (
            "These investments offer balanced risk and return, but "
            "market fluctuations can still impact performance."
            "Investment risk depends on asset type and market factors."
        )

    # Fallback explanation
    else:
        explanation = (
            "Investment risk depends on asset type, market conditions, "
            "and your investment horizon."
        )

    # -------------------------
    # Step 6: Final response
    # -------------------------
    tip = get_risk_tip(risk_level=risk_level.lower())

    return set_state(
        state,
        start,
        answer=f"Risk Level: {risk_level}\n{explanation}\n\n{tip}",
        agent="risk_agent",
        confidence=0.8,
        decision_source="rule",
        answer_source="risk_logic",
        trace_action="classify",
        extra={
        "risk_level": risk_level,
        "risk_explanation": explanation
        }
    )