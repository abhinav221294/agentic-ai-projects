"""
Test file for agent detection

Covers:
- Single agent triggers
- Multi-agent triggers
- No-agent scenarios
- Ambiguous queries
"""

test_cases = [

    # -------------------------
    # NO AGENTS (pure advisor logic)
    # -------------------------
    {
        "query": "I want to invest 20k monthly with moderate risk, suggest a plan",
        "intent": "allocation",
        "expected_agents": []
    },
    {
        "query": "How should I diversify my portfolio for long term stability?",
        "intent": "advice",
        "expected_agents": []
    },

    # -------------------------
    # MARKET AGENT
    # -------------------------
    {
        "query": "Which companies are performing well right now for investment?",
        "intent": "news_invest",
        "expected_agents": ["market_agent"]
    },
    {
        "query": "Should I invest in tech stocks given current market trends?",
        "intent": "news_invest",
        "expected_agents": ["market_agent"]
    },

    # -------------------------
    # NEWS AGENT
    # -------------------------
    {
        "query": "What recent economic changes could impact my investments?",
        "intent": "general_news",
        "expected_agents": ["news_agent"]
    },
    {
        "query": "Are there any global trends affecting equity markets right now?",
        "intent": "general_news",
        "expected_agents": ["news_agent"]
    },

    # -------------------------
    # MARKET + NEWS (combined)
    # -------------------------
    {
        "query": "Based on current market and news, where should I invest?",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "news_agent"]
    },
    {
        "query": "Considering recent trends and stock performance, suggest good investments",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "news_agent"]
    },

    # -------------------------
    # RISK AGENT
    # -------------------------
    {
        "query": "I want high returns but I am not sure how much risk I can take",
        "intent": "advice",
        "expected_agents": ["risk_agent"]
    },
    {
        "query": "Help me understand my risk tolerance before investing",
        "intent": "advice",
        "expected_agents": ["risk_agent"]
    },

    # -------------------------
    # RAG AGENT (explanations / conflict)
    # -------------------------
    {
        "query": "Why is this allocation better than putting everything in equity?",
        "intent": "advice",
        "expected_agents": ["rag_agent"]
    },
    {
        "query": "Explain why diversification is important in my portfolio",
        "intent": "advice",
        "expected_agents": ["rag_agent"]
    },

    # -------------------------
    # COMPLEX MULTI-AGENT CASES
    # -------------------------
    {
        "query": "Given current market conditions and my moderate risk, suggest where I should invest",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "news_agent"]
    },
    {
        "query": "I am confused between safety and returns, and also want to consider market trends",
        "intent": "advice",
        "expected_agents": ["risk_agent", "news_agent"]
    },

    # -------------------------
    # EDGE CASES
    # -------------------------
    {
        "query": "Should I invest now or wait for better opportunities?",
        "intent": "advice",
        "expected_agents": ["news_agent"]
    },
    {
        "query": "I want to invest aggressively but still be safe, what should I do?",
        "intent": "advice",
        "expected_agents": ["risk_agent"]
    }
]


def compare_agents(predicted, expected):
    return set(predicted) == set(expected)


def run_agent_tests(detect_agents_fn, state, llm):
    correct = 0

    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        intent = case["intent"]
        expected = case["expected_agents"]

        state["query"] = query

        predicted = detect_agents_fn(query, state, intent, llm)

        result = "✅" if compare_agents(predicted, expected) else "❌"

        print(f"{i}. {result}")
        print(f"Query: {query}")
        print(f"Intent: {intent}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}\n")

        if compare_agents(predicted, expected):
            correct += 1

    print(f"\nAccuracy: {correct}/{len(test_cases)}")


if __name__ == "__main__":
    from utils.llm import get_llm
    from dotenv import load_dotenv
    load_dotenv()

    llm = get_llm(temperature=0)
    state = {}

    from agents.advisor_agent import detect_agents_llm  # update path

    run_agent_tests(detect_agents_llm, state, llm)