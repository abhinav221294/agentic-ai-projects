"""
Comprehensive End-to-End Advisor Evaluation Suite

Covers:
- Suggestion flow
- Projection flow
- Execution flow
- Market/news enrichment
- Risk handling
- Modify flow
- Ambiguous queries
- Multi-turn memory
- Invalid inputs
- Hallucination resistance
- Agent orchestration
- Conversational continuity
- Edge cases
"""

# =========================================================
# TEST CASES
# =========================================================

test_cases = [

    # =====================================================
    # SUGGESTION FLOW
    # =====================================================

    {
        "query": "I want to invest 10000 monthly with medium risk for growth",
        "checks": [
            "allocation_present",
            "amount_split_present",
            "funds_present"
        ]
    },

    {
        "query": "I can invest 25000 monthly with high risk appetite for long term wealth creation through SIP",
        "checks": [
            "allocation_present",
            "amount_split_present",
            "funds_present",
            "risk_guidance_present"
        ]
    },

    {
        "query": "I want a diversified investment portfolio with medium risk and long term growth",
        "checks": [
            "allocation_present",
            "funds_present",
            "balanced_advice_present"
        ]
    },

    # =====================================================
    # PROJECTION FLOW
    # =====================================================

    {
        "query": "If I invest 10000 monthly what returns can I expect in 10 years?",
        "checks": [
            "projection_present",
            "numbers_present"
        ]
    },

    {
        "query": "If I invest 500000 lump sum with high risk what can it grow to in 15 years?",
        "checks": [
            "projection_present",
            "numbers_present"
        ]
    },

    {
        "query": "How much wealth can I create in 20 years if I invest aggressively with SIP?",
        "checks": [
            "projection_present"
        ]
    },

    # =====================================================
    # EXECUTION FLOW
    # =====================================================

    {
        "query": "yes go ahead with the plan",
        "checks": [
            "execution_steps_present"
        ]
    },

    {
        "query": "start the investment process",
        "checks": [
            "execution_steps_present"
        ]
    },

    # =====================================================
    # MARKET + NEWS ENRICHMENT
    # =====================================================

    {
        "query": "Where should I invest based on current market and news?",
        "checks": [
            "allocation_present",
            "market_insight_present",
            "news_present"
        ]
    },

    {
        "query": "Considering inflation, interest rates, and current market uncertainty, where should I invest for long term growth?",
        "checks": [
            "market_insight_present",
            "news_present",
            "risk_guidance_present"
        ]
    },

    {
        "query": "Should I invest in technology stocks given current economic conditions and AI trends?",
        "checks": [
            "market_insight_present",
            "news_present"
        ]
    },

    # =====================================================
    # STOCK / MARKET AGENT TESTS
    # =====================================================

    {
        "query": "How is Tesla performing recently?",
        "checks": [
            "market_insight_present"
        ]
    },

    {
        "query": "What do you think about Reliance and TCS for long term investing?",
        "checks": [
            "market_insight_present"
        ]
    },

    {
        "query": "Should I invest in Apple stock now or wait for better market conditions?",
        "checks": [
            "market_insight_present",
            "news_present"
        ]
    },

    # =====================================================
    # RISK HANDLING
    # =====================================================

    {
        "query": "I want high returns but I am not sure about risk",
        "checks": [
            "risk_guidance_present"
        ]
    },

    {
        "query": "I want guaranteed high returns with zero risk",
        "checks": [
            "risk_guidance_present"
        ]
    },

    {
        "query": "I want aggressive growth but I cannot tolerate losses",
        "checks": [
            "risk_guidance_present"
        ]
    },

    # =====================================================
    # MODIFY FLOW
    # =====================================================

    {
        "query": "Change this to lump sum investment of 200000",
        "checks": [
            "allocation_present",
            "amount_split_present"
        ]
    },

    {
        "query": "Change my risk profile to high risk",
        "checks": [
            "allocation_present",
            "risk_guidance_present"
        ]
    },

    {
        "query": "Modify the plan for income generation instead of growth",
        "checks": [
            "allocation_present"
        ]
    },

    # =====================================================
    # EDGE CASES / AMBIGUOUS
    # =====================================================

    {
        "query": "I want good returns but also safety, what should I do?",
        "checks": [
            "balanced_advice_present"
        ]
    },

    {
        "query": "Markets look uncertain and inflation is rising, should I wait or invest now?",
        "checks": [
            "news_present",
            "risk_guidance_present"
        ]
    },

    {
        "query": "I am confused between safety and growth",
        "checks": [
            "balanced_advice_present",
            "risk_guidance_present"
        ]
    },

    # =====================================================
    # MEMORY / MULTI-TURN TESTS
    # =====================================================

    {
        "query": "I want to invest with medium risk",
        "checks": [
            "clarification_present"
        ]
    },

    {
        "query": "growth",
        "checks": [
            "clarification_present"
        ]
    },

    {
        "query": "sip",
        "checks": [
            "clarification_present"
        ]
    },

    {
        "query": "10000",
        "checks": [
            "allocation_present",
            "amount_split_present"
        ]
    },

    # =====================================================
    # INVALID INPUTS
    # =====================================================

    {
        "query": "",
        "checks": [
            "invalid_input_present"
        ]
    },

    {
        "query": "asdfghjkl",
        "checks": [
            "clarification_present"
        ]
    },

    {
        "query": "put 200% into crypto and 150% into equity",
        "checks": [
            "allocation_limit_warning"
        ]
    },

    # =====================================================
    # HALLUCINATION / SAFETY
    # =====================================================

    {
        "query": "Suggest a guaranteed 50% yearly return investment",
        "checks": [
            "risk_guidance_present"
        ]
    },

    {
        "query": "How can I double my money in one month safely?",
        "checks": [
            "risk_guidance_present"
        ]
    },

    # =====================================================
    # LONG COMPLEX REALISTIC QUERIES
    # =====================================================

    {
        "query": (
            "I am 28 years old and can invest 35000 monthly through SIP. "
            "I have medium to high risk tolerance and want long term wealth creation "
            "for financial independence in the next 20 years. "
            "Considering inflation, current market uncertainty, interest rates, "
            "and AI sector growth, suggest a diversified portfolio allocation and explain why."
        ),
        "checks": [
            "allocation_present",
            "amount_split_present",
            "market_insight_present",
            "news_present",
            "risk_guidance_present",
            "funds_present"
        ]
    },

    {
        "query": (
            "I recently received a 10 lakh bonus and want to invest it wisely. "
            "I do not want extremely high risk but I also don't want my money sitting idle. "
            "Please suggest a balanced long term investment strategy considering "
            "economic slowdown concerns and market volatility."
        ),
        "checks": [
            "allocation_present",
            "amount_split_present",
            "risk_guidance_present",
            "news_present"
        ]
    },

    {
        "query": (
            "Given the current AI boom, rising inflation, global uncertainty, "
            "and interest rate environment, should I focus more on equity, debt, "
            "or gold if my goal is long term wealth creation with moderate risk?"
        ),
        "checks": [
            "allocation_present",
            "market_insight_present",
            "news_present",
            "risk_guidance_present"
        ]
    }
]


# =========================================================
# CHECK FUNCTIONS
# =========================================================

def check_allocation(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "allocation",
            "% equity",
            "% debt",
            "suggested allocation",
            "diversification"
        ]
    )


def check_amount_split(answer):
    answer = answer.lower()

    return (
        "₹" in answer
        or "rs" in answer
        or "monthly sip" in answer
        or "lump sum" in answer
    )


def check_funds(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "fund",
            "sip",
            "index fund",
            "flexi cap",
            "mutual fund"
        ]
    )


def check_projection(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "future value",
            "10 years",
            "15 years",
            "projection",
            "return"
        ]
    )


def check_numbers(answer):
    import re
    return bool(re.search(r"\d{2,}", answer))


def check_execution(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "step",
            "start",
            "invest",
            "broker",
            "auto-debit",
            "review portfolio"
        ]
    )


def check_market(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "market",
            "stock",
            "trend",
            "trading",
            "sector"
        ]
    )


def check_news(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "news",
            "trend",
            "inflation",
            "interest rates",
            "economic",
            "uncertainty"
        ]
    )


def check_risk(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "risk",
            "risk tolerance",
            "risk profile",
            "higher risk",
            "lower risk",
            "volatility"
        ]
    )


def check_balanced(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "balance",
            "balanced",
            "divers",
            "mix",
            "allocation"
        ]
    )


def check_clarification(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "please share",
            "can you share",
            "tell me",
            "need more information",
            "risk level",
            "goal"
        ]
    )


def check_invalid_input(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "invalid",
            "please enter",
            "couldn't understand",
            "try again"
        ]
    )


def check_allocation_limit(answer):
    answer = answer.lower()

    return any(
        x in answer
        for x in [
            "exceeds 100%",
            "capped",
            "reduce risk",
            "adjust"
        ]
    )


# =========================================================
# TEST RUNNER
# =========================================================

def run_answer_tests(advisor_agent, state):

    check_map = {
        "allocation_present": check_allocation,
        "amount_split_present": check_amount_split,
        "funds_present": check_funds,
        "projection_present": check_projection,
        "numbers_present": check_numbers,
        "execution_steps_present": check_execution,
        "market_insight_present": check_market,
        "news_present": check_news,
        "risk_guidance_present": check_risk,
        "balanced_advice_present": check_balanced,
        "clarification_present": check_clarification,
        "invalid_input_present": check_invalid_input,
        "allocation_limit_warning": check_allocation_limit
    }

    correct = 0

    for i, case in enumerate(test_cases, 1):

        query = case["query"]
        checks = case["checks"]

        state["query"] = query

        result_state = advisor_agent(state)
        answer = result_state.get("answer", "")

        passed_all = True

        print(f"\n{i}. Query: {query}")

        for check in checks:

            fn = check_map[check]
            res = fn(answer)

            print(f"   {check}: {'✅' if res else '❌'}")

            if not res:
                passed_all = False

        if passed_all:
            correct += 1

    print(f"\nFinal Score: {correct}/{len(test_cases)}")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    from agents.advisor_agent import advisor_agent
    from dotenv import load_dotenv

    load_dotenv()

    state = {}

    run_answer_tests(advisor_agent, state)