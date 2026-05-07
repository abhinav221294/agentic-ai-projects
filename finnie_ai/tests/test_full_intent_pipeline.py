"""
Test file for FULL hierarchical intent pipeline.

Tests:
- execution
- modify
- projection
- allocation
- advice
- news_invest
- general_news
"""

# =====================================================
# TEST CASES
# =====================================================

test_cases = [

    # =================================================
    # EXECUTION
    # =================================================

    {
        "query": "yes go ahead",
        "expected_intent": "execution"
    },

    {
        "query": "continue with the plan",
        "expected_intent": "execution"
    },

    {
        "query": "start the investment process",
        "expected_intent": "execution"
    },

    # =================================================
    # MODIFY
    # =================================================

    {
        "query": "change my risk to high",
        "expected_intent": "modify"
    },

    {
        "query": "switch this to SIP",
        "expected_intent": "modify"
    },

    {
        "query": "increase monthly amount to 25000",
        "expected_intent": "modify"
    },

    # =================================================
    # PROJECTION
    # =================================================

    {
        "query": "How much wealth can I create in 20 years?",
        "expected_intent": "projection"
    },

    {
        "query": "What returns can I expect in 15 years?",
        "expected_intent": "projection"
    },

    {
        "query": "Will this grow enough for retirement?",
        "expected_intent": "projection"
    },

    # =================================================
    # ALLOCATION
    # =================================================

    {
        "query": "Suggest a portfolio for medium risk",
        "expected_intent": "allocation"
    },

    {
        "query": "How should I diversify my investments?",
        "expected_intent": "allocation"
    },

    # =================================================
    # ADVICE
    # =================================================

    {
        "query": "Should I invest now or wait?",
        "expected_intent": "advice"
    },

    {
        "query": "I want safe returns with low risk",
        "expected_intent": "advice"
    },

    # =================================================
    # NEWS INVEST
    # =================================================

    {
        "query": "Where should I invest during inflation?",
        "expected_intent": "news_invest"
    },

    {
        "query": "Best sectors in current market conditions?",
        "expected_intent": "news_invest"
    },

    # =================================================
    # GENERAL NEWS
    # =================================================

    {
        "query": "What is happening in the stock market?",
        "expected_intent": "general_news"
    },

    {
        "query": "Latest AI market trends?",
        "expected_intent": "general_news"
    },

# =================================================
# COMPLEX EXECUTION
# =================================================

{
    "query": (
        "The portfolio allocation looks reasonable and aligns "
        "with my retirement goals. Let's proceed with the investment setup."
    ),
    "expected_intent": "execution"
},

{
    "query": (
        "I reviewed the suggested funds and risk distribution. "
        "Please continue with the next investment steps."
    ),
    "expected_intent": "execution"
},

# =================================================
# COMPLEX MODIFY
# =================================================

{
    "query": (
        "Considering the current market volatility, reduce my equity exposure "
        "slightly and make the portfolio more balanced."
    ),
    "expected_intent": "modify"
},

{
    "query": (
        "Instead of aggressive growth, I now want a more conservative "
        "income-oriented investment strategy."
    ),
    "expected_intent": "modify"
},

{
    "query": (
        "Change the monthly SIP amount from 10k to 25k and "
        "increase international exposure."
    ),
    "expected_intent": "modify"
},

# =================================================
# COMPLEX PROJECTION
# =================================================

{
    "query": (
        "If I consistently invest 35000 monthly through SIP with medium risk, "
        "how much wealth can I realistically create over the next 20 years?"
    ),
    "expected_intent": "projection"
},

{
    "query": (
        "Will this investment strategy generate enough corpus "
        "for early retirement considering inflation?"
    ),
    "expected_intent": "projection"
},

{
    "query": (
        "Assuming moderate annual returns, what could my portfolio "
        "potentially grow to in 15 years?"
    ),
    "expected_intent": "projection"
},

# =================================================
# COMPLEX ALLOCATION
# =================================================

{
    "query": (
        "I am 30 years old with medium risk tolerance and a long-term "
        "wealth creation goal. How should I allocate my investments "
        "across equity, debt, and gold?"
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "Suggest a diversified investment portfolio for someone "
        "looking for long-term growth with controlled risk."
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "How should I structure my portfolio if I want exposure "
        "to both Indian and US markets?"
    ),
    "expected_intent": "allocation"
},

# =================================================
# COMPLEX ADVICE
# =================================================

{
    "query": (
        "Markets seem highly uncertain right now and I am confused "
        "whether I should invest immediately or wait for better opportunities."
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "I want reasonable returns but I also want to avoid "
        "major losses during market downturns."
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "Given rising inflation and economic slowdown concerns, "
        "does it make sense to stay invested long term?"
    ),
    "expected_intent": "advice"
},

# =================================================
# COMPLEX NEWS INVEST
# =================================================

{
    "query": (
        "Considering current inflation trends, interest rates, "
        "and AI sector growth, where should I invest right now?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "Which investment sectors are likely to benefit "
        "from current global economic conditions?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "Given recession fears and market uncertainty, "
        "what investments look attractive currently?"
    ),
    "expected_intent": "news_invest"
},

# =================================================
# COMPLEX GENERAL NEWS
# =================================================

{
    "query": (
        "What are the latest developments impacting global "
        "financial markets and technology stocks?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "How are inflation and interest rate changes "
        "affecting markets globally?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "What are analysts currently saying about the AI sector "
        "and future market trends?"
    ),
    "expected_intent": "general_news"
},

# =================================================
# AMBIGUOUS / EDGE CASES
# =================================================

{
    "query": (
        "I want high returns but I really don't want to take much risk. "
        "What should I do?"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "Can you suggest investments that are safe but still "
        "grow faster than traditional savings?"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "I have 15 lakh available for investment and want a diversified "
        "long-term portfolio with moderate risk."
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "If I invest aggressively now, can I potentially achieve "
        "financial independence within 15 years?"
    ),
    "expected_intent": "projection"
},

{
    "query": (
        "Should I focus more on gold, equity, or debt considering "
        "today's economic uncertainty?"
    ),
    "expected_intent": "news_invest"
},

# =================================================
# NOISY / REALISTIC USER LANGUAGE
# =================================================

{
    "query": (
        "hmm okay so like if I invest regularly every month "
        "what are the chances this actually becomes meaningful wealth later?"
    ),
    "expected_intent": "projection"
},

{
    "query": (
        "uh markets kinda scary right now so idk if I should wait "
        "or just start slowly investing"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "thinking maybe medium risk and long term growth "
        "what portfolio would make sense?"
    ),
    "expected_intent": "allocation"
},

# =================================================
# CONTEXT-LIKE FOLLOWUPS
# =================================================

{
    "query": (
        "okay that allocation seems reasonable, what next?"
    ),
    "expected_intent": "execution"
},

{
    "query": (
        "actually lower the risk slightly and reduce equity exposure"
    ),
    "expected_intent": "modify"
}
]


# =====================================================
# TEST RUNNER
# =====================================================

def run_full_pipeline_tests(
    detect_intent_llm,
    state,
    llm
):

    correct = 0

    for i, case in enumerate(test_cases, 1):

        query = case["query"]
        expected = case["expected_intent"]

        state["query"] = query

        predicted = detect_intent_llm(
            query=query,
            state=state,
            llm=llm
        )

        result = "✅" if predicted == expected else "❌"

        print(f"{i}. {result}")
        print(f"Query: {query}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}\n")

        if predicted == expected:
            correct += 1

    print(f"\nAccuracy: {correct}/{len(test_cases)}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    from dotenv import load_dotenv
    from utils.llm import get_llm

    load_dotenv()

    llm = get_llm(temperature=0)

    state = {}

    from agents.advisor_agent import detect_intent_llm

    run_full_pipeline_tests(
        detect_intent_llm,
        state,
        llm
    )