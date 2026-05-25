# Enhanced Agent Detection Test Suite

"""
Enhanced test file for advisor agent detection

Covers:
- No agent calls
- Single agent calls
- Pair combinations
- Triple combinations
- All agent combinations
- Ambiguous queries
- Conflict-based reasoning
- Explanation-based reasoning
"""

from itertools import combinations


# =========================================================
# TEST CASES
# =========================================================

test_cases = [

    # =====================================================
    # NO AGENT
    # =====================================================
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
    {
        "query": "I have some savings sitting idle, what should I do?",
        "intent": "advice",
        "expected_agents": []
    },


    # =====================================================
    # SINGLE AGENT — MARKET
    # =====================================================
    {
        "query": "Which companies are performing well right now for investment?",
        "intent": "news_invest",
        "expected_agents": ["market_agent"]
    },
    {
        "query": "Should I invest in tech stocks given current market trends?",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "news_agent"]
    },


    # =====================================================
    # SINGLE AGENT — NEWS
    # =====================================================
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


    # =====================================================
    # SINGLE AGENT — RISK
    # =====================================================
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


    # =====================================================
    # SINGLE AGENT — RAG
    # =====================================================
    {
        "query": "Explain why diversification is important in my portfolio",
        "intent": "advice",
        "expected_agents": ["rag_agent"]
    },
    {
        "query": "Why is this allocation better than putting everything in equity?",
        "intent": "advice",
        "expected_agents": ["rag_agent"]
    },


    # =====================================================
    # MARKET + NEWS
    # =====================================================
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


    # =====================================================
    # MARKET + RISK
    # =====================================================
    {
        "query": "Which stocks fit my moderate risk profile?",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "risk_agent"]
    },
    {
        "query": "Suggest growth stocks suitable for conservative investors",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "risk_agent"]
    },


    # =====================================================
    # MARKET + RAG
    # =====================================================
    {
        "query": "Explain why these stocks are performing well",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "rag_agent"]
    },
    {
        "query": "Why are banking stocks rising recently?",
        "intent": "news_invest",
        "expected_agents": ["news_agent", "rag_agent", "market_agent"]
    },


    # =====================================================
    # NEWS + RISK
    # =====================================================
    {
        "query": "Given current economic uncertainty, how should I manage risk?",
        "intent": "advice",
        "expected_agents": ["risk_agent", "news_agent", "rag_agent"]
    },
    {
        "query": "I am confused between safety and returns, and also want to consider market trends",
        "intent": "advice",
        "expected_agents": ["news_agent", "risk_agent"]
    },


    # =====================================================
    # NEWS + RAG
    # =====================================================
    {
        "query": "Explain recent economic trends and how they affect investments",
        "intent": "general_news",
        "expected_agents": ["news_agent", "rag_agent"]
    },
    {
        "query": "Why is inflation impacting equity markets?",
        "intent": "general_news",
        "expected_agents": ["news_agent", "rag_agent"]
    },


    # =====================================================
    # RISK + RAG
    # =====================================================
    {
        "query": "Explain why aggressive investing may not suit my profile",
        "intent": "advice",
        "expected_agents": ["risk_agent", "rag_agent"]
    },
    {
        "query": "Help me understand why my risk tolerance matters",
        "intent": "advice",
        "expected_agents": ["risk_agent", "rag_agent"]
    },


    # =====================================================
    # MARKET + NEWS + RISK
    # =====================================================
    {
        "query": "Based on market trends and news, what investments suit my risk level?",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "news_agent", "risk_agent"]
    },


    # =====================================================
    # MARKET + NEWS + RAG
    # =====================================================
    {
        "query": "Explain why these stocks are performing well based on current market news",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "news_agent", "rag_agent"]
    },


    # =====================================================
    # NEWS + RISK + RAG
    # =====================================================
    {
        "query": "Given economic uncertainty, explain how I should manage investment risk",
        "intent": "advice",
        "expected_agents": ["news_agent", "risk_agent", "rag_agent"]
    },


    # =====================================================
    # MARKET + RISK + RAG
    # =====================================================
    {
        "query": "Explain which stocks suit my moderate risk appetite and why",
        "intent": "news_invest",
        "expected_agents": ["market_agent", "risk_agent", "rag_agent"]
    },


    # =====================================================
    # ALL AGENTS
    # =====================================================
    {
        "query": "Considering my risk tolerance, current market trends, and recent news, explain where I should invest and why",
        "intent": "news_invest",
        "expected_agents": [
            "market_agent",
            "news_agent",
            "risk_agent",
            "rag_agent"
        ]
    },


    # =====================================================
    # EDGE / AMBIGUOUS CASES
    # =====================================================
    {
        "query": "Should I invest now or wait for better opportunities?",
        "intent": "advice",
        "expected_agents": ["news_agent"]
    },
    {
        "query": "I want aggressive growth but still want safety",
        "intent": "advice",
        "expected_agents": ["risk_agent"]
    },
    {
        "query": "Things look uncertain, how should I invest?",
        "intent": "advice",
        "expected_agents": ["news_agent"]
    },
]


# =========================================================
# METRICS
# =========================================================

def compare_agents(predicted, expected):
    return set(predicted) == set(expected)


# =========================================================
# TEST RUNNER
# =========================================================

def run_agent_tests(detect_agents_fn, state, llm):

    correct = 0

    total_tp = 0
    total_fp = 0
    total_fn = 0

    for i, case in enumerate(test_cases, 1):

        query = case["query"]
        intent = case["intent"]

        expected = set(case["expected_agents"])

        state["query"] = query

        predicted = set(
            detect_agents_fn(query, state, intent, llm)
        )

        result = "✅" if predicted == expected else "❌"

        print(f"{i}. {result}")
        print(f"Query: {query}")
        print(f"Intent: {intent}")
        print(f"Expected: {list(expected)}")
        print(f"Predicted: {list(predicted)}")

        missing = expected - predicted
        extra = predicted - expected

        if missing:
            print(f"Missing : {list(missing)}")

        if extra:
            print(f"Extra   : {list(extra)}")

        print()

        # Accuracy
        if predicted == expected:
            correct += 1

        # Metrics
        tp = len(predicted & expected)
        fp = len(predicted - expected)
        fn = len(expected - predicted)

        total_tp += tp
        total_fp += fp
        total_fn += fn

    accuracy = correct / len(test_cases)

    precision = (
        total_tp / (total_tp + total_fp)
        if (total_tp + total_fp) > 0
        else 0
    )

    recall = (
        total_tp / (total_tp + total_fn)
        if (total_tp + total_fn) > 0
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    print("\n====================")
    print(f"Accuracy : {correct}/{len(test_cases)} = {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall   : {recall:.2f}")
    print(f"F1 Score : {f1:.2f}")
    print("====================")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    from dotenv import load_dotenv

    from utils.llm import get_llm

    load_dotenv()

    llm = get_llm(temperature=0)

    state = {}

    from agents.advisor_agent import detect_agents_llm

    run_agent_tests(
        detect_agents_llm,
        state,
        llm
    )