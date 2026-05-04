"""
Test file for final answer relevance

Covers:
- End-to-end advisor behavior
- Intent → Stage → Response correctness
- Agent enrichment presence
- Completeness of answer
"""

test_cases = [

    # -------------------------
    # SUGGESTION FLOW
    # -------------------------
    {
        "query": "I want to invest 10000 monthly with medium risk for growth",
        "checks": [
            "allocation_present",
            "amount_split_present",
            "funds_present"
        ]
    },

    # -------------------------
    # PROJECTION FLOW
    # -------------------------
    {
        "query": "If I invest 10000 monthly what returns can I expect in 10 years?",
        "checks": [
            "projection_present",
            "numbers_present"
        ]
    },

    # -------------------------
    # EXECUTION FLOW
    # -------------------------
    {
        "query": "yes go ahead with the plan",
        "checks": [
            "execution_steps_present"
        ]
    },

    # -------------------------
    # MARKET + NEWS ENRICHMENT
    # -------------------------
    {
        "query": "Where should I invest based on current market and news?",
        "checks": [
            "allocation_present",
            "market_insight_present",
            "news_present"
        ]
    },

    # -------------------------
    # RISK HANDLING
    # -------------------------
    {
        "query": "I want high returns but I am not sure about risk",
        "checks": [
            "risk_guidance_present"
        ]
    },

    # -------------------------
    # MODIFY FLOW
    # -------------------------
    {
        "query": "Change this to lump sum investment of 200000",
        "checks": [
            "allocation_present",
            "amount_split_present"
        ]
    },

    # -------------------------
    # EDGE CASE (AMBIGUOUS)
    # -------------------------
    {
        "query": "I want good returns but also safety, what should I do?",
        "checks": [
            "balanced_advice_present"
        ]
    }
]

def check_allocation(answer):
    return any(x in answer.lower() for x in ["allocation", "% equity", "% debt"])

def check_amount_split(answer):
    return "₹" in answer or "rs" in answer.lower()

def check_funds(answer):
    return "fund" in answer.lower()

def check_projection(answer):
    return any(x in answer.lower() for x in ["future value", "in 10 years", "return"])

def check_numbers(answer):
    import re
    return bool(re.search(r"\d{2,}", answer))

def check_execution(answer):
    return any(x in answer.lower() for x in ["step", "start", "invest"])

def check_market(answer):
    return "market" in answer.lower()

def check_news(answer):
    return "news" in answer.lower() or "trend" in answer.lower()

def check_risk(answer):
    return "risk" in answer.lower()

def check_balanced(answer):
    return "balance" in answer.lower() or "divers" in answer.lower()

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
        "balanced_advice_present": check_balanced
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




if __name__ == "__main__":
    from agents.advisor_agent import advisor_agent   # ⚠️ update this import
    from dotenv import load_dotenv
    load_dotenv()
    state = {}

    run_answer_tests(advisor_agent, state)