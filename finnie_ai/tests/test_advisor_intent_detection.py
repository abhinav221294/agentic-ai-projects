"""
Test file for intent detection (advisor-focused)

Covers:
- Ambiguous queries
- Multi-intent queries
- Context-dependent queries
- Real-world phrasing
"""

test_cases = [

    # -------------------------
    # ADVICE (general but not trivial)
    # -------------------------
    {
        "query": "I have some savings sitting idle, how should I start investing wisely?",
        "expected_intent": "advice"
    },
    {
        "query": "Given inflation and market volatility, where should I put my money?",
        "expected_intent": "advice"
    },

    # -------------------------
    # ALLOCATION (portfolio intent)
    # -------------------------
    {
        "query": "I want to invest 50k monthly with moderate risk, how should I allocate it?",
        "expected_intent": "allocation"
    },
    {
        "query": "Can you suggest a good portfolio mix for long term wealth creation?",
        "expected_intent": "allocation"
    },
    {
        "query": "I prefer equity heavy investment but still want some safety, how should I split?",
        "expected_intent": "allocation"
    },

    # -------------------------
    # PROJECTION (returns/future)
    # -------------------------
    {
        "query": "If I invest 10k every month, how much can I expect in 15 years?",
        "expected_intent": "projection"
    },
    {
        "query": "What kind of returns can I realistically expect with medium risk?",
        "expected_intent": "projection"
    },
    {
        "query": "Will this investment grow enough for retirement in 20 years?",
        "expected_intent": "projection"
    },

    # -------------------------
    # EXECUTION (action intent)
    # -------------------------
    {
        "query": "Okay that sounds good, let’s go ahead with this plan",
        "expected_intent": "execution"
    },
    {
        "query": "I’m ready to invest, what should I do next?",
        "expected_intent": "execution"
    },
    {
        "query": "Start the investment with the suggested funds",
        "expected_intent": "execution"
    },

    # -------------------------
    # MODIFY (profile change)
    # -------------------------
    {
        "query": "Actually I want to take higher risk now, adjust the plan",
        "expected_intent": "modify"
    },
    {
        "query": "Change it to lump sum instead of SIP",
        "expected_intent": "modify"
    },
    {
        "query": "Make it more income focused instead of growth",
        "expected_intent": "modify"
    },

    # -------------------------
    # NEWS-BASED INVESTING
    # -------------------------
    {
        "query": "Considering recent market trends, where should I invest now?",
        "expected_intent": "news_invest"
    },
    {
        "query": "Based on current economic conditions, what sectors look promising?",
        "expected_intent": "news_invest"
    },

    # -------------------------
    # GENERAL NEWS (non-investment decision)
    # -------------------------
    {
        "query": "What are the latest developments affecting investments globally?",
        "expected_intent": "general_news"
    },

    # -------------------------
    # HARD / EDGE CASES
    # -------------------------
    {
        "query": "I want good returns but don’t want to take much risk, what should I do?",
        "expected_intent": "advice"
    },
    {
        "query": "If I follow your plan, will I beat inflation in the long run?",
        "expected_intent": "projection"
    },
    {
        "query": "Does it make sense to invest now or wait for correction?",
        "expected_intent": "advice"
    },
    {
        "query": "Given my goal is income but I can tolerate some risk, how should I invest?",
        "expected_intent": "allocation"
    },

     # -------------------------
    # MULTI-INTENT (should pick dominant)
    # -------------------------
    {
        "query": "I have 50k monthly, medium risk, can you suggest allocation and expected returns?",
        "expected_intent": "allocation"  # dominant = allocation
    },
    {
        "query": "Suggest a portfolio and also tell me how much it will grow in 10 years",
        "expected_intent": "allocation"
    },

    # -------------------------
    # CONTEXT-DEPENDENT (should rely on memory)
    # -------------------------
    {
        "query": "yes let's continue",
        "expected_intent": "execution"
    },
    {
        "query": "okay what next?",
        "expected_intent": "execution"
    },

    # -------------------------
    # AMBIGUOUS HUMAN LANGUAGE
    # -------------------------
    {
        "query": "I don’t want to lose money but still want decent returns, what do you suggest?",
        "expected_intent": "advice"
    },
    {
        "query": "I want something safe but not too slow growing",
        "expected_intent": "advice"
    },

    # -------------------------
    # PARTIAL PROFILE INPUT
    # -------------------------
    {
        "query": "I can invest 20k monthly, what should I do?",
        "expected_intent": "advice"
    },
    {
        "query": "My risk is high, where should I invest?",
        "expected_intent": "allocation"
    },

    # -------------------------
    # CONFLICTING SIGNALS
    # -------------------------
    {
        "query": "I want high returns but zero risk, how should I invest?",
        "expected_intent": "allocation"
    },

    # -------------------------
    # TIMING vs NEWS CONFUSION
    # -------------------------
    {
        "query": "Market seems unstable, should I wait or invest now?",
        "expected_intent": "advice"
    },
    {
        "query": "Given recession fears, where should I invest?",
        "expected_intent": "news_invest"
    },

    # -------------------------
    # PROJECTION WITHOUT NUMBERS
    # -------------------------
    {
        "query": "Will this plan be enough for my retirement?",
        "expected_intent": "projection"
    },

    # -------------------------
    # MODIFY (subtle)
    # -------------------------
    {
        "query": "Actually reduce risk a bit and make it more balanced",
        "expected_intent": "modify"
    },

    # -------------------------
    # NOISY / REAL USER INPUT
    # -------------------------
    {
        "query": "hmm ok so like if I put money monthly like 10k ish what happens long term?",
        "expected_intent": "projection"
    },
    {
        "query": "uh I think I want safer option maybe not too aggressive what do you say",
        "expected_intent": "advice"
    },

    # -------------------------
    # SHORT / FRAGMENTED
    # -------------------------
    {
        "query": "next step?",
        "expected_intent": "execution"
    },
    {
        "query": "returns?",
        "expected_intent": "projection"
    }
]


def run_intent_tests(detect_intent_fn, state, llm):
    correct = 0

    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        expected = case["expected_intent"]

        state["query"] = query

        predicted = detect_intent_fn(query, state, llm)

        result = "✅" if predicted == expected else "❌"

        print(f"{i}. {result}")
        print(f"Query: {query}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}\n")

        if predicted == expected:
            correct += 1

    print(f"\nAccuracy: {correct}/{len(test_cases)}")


if __name__ == "__main__":
    from utils.llm import get_llm
    from dotenv import load_dotenv
    load_dotenv()
    llm = get_llm(temperature=0)
    state = {}

    from agents.advisor_agent import detect_intent_llm  # update path

    run_intent_tests(detect_intent_llm, state, llm)