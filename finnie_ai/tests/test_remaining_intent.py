"""
Test file for detect_remaining_intent()

ONLY tests:
- allocation
- advice
- news_invest
- general_news

execution / modify / projection
are handled earlier in hierarchy.
"""

# =====================================================
# TEST CASES
# =====================================================

test_cases = [

    # =================================================
    # ALLOCATION
    # =================================================

    {
        "query": "I want to invest 50k monthly with moderate risk",
        "expected_intent": "allocation"
    },

    {
        "query": "Suggest a diversified portfolio for long term growth",
        "expected_intent": "allocation"
    },

    {
        "query": "How should I split investments across equity and debt?",
        "expected_intent": "allocation"
    },

    {
        "query": "Recommend funds for medium risk investing",
        "expected_intent": "allocation"
    },

    {
        "query": "I want a balanced portfolio allocation",
        "expected_intent": "allocation"
    },

    # =================================================
    # ADVICE
    # =================================================

    {
        "query": "I want decent returns with low risk",
        "expected_intent": "advice"
    },

    {
        "query": "Should I invest now or wait?",
        "expected_intent": "advice"
    },

    {
        "query": "Markets seem uncertain, what should I do?",
        "expected_intent": "advice"
    },

    {
        "query": "I want safety but also some growth",
        "expected_intent": "advice"
    },

    {
        "query": "I am confused between safety and returns",
        "expected_intent": "advice"
    },

    # =================================================
    # NEWS INVEST
    # =================================================

    {
        "query": "Where should I invest given current inflation?",
        "expected_intent": "news_invest"
    },

    {
        "query": "Which sectors look good during recession fears?",
        "expected_intent": "news_invest"
    },

    {
        "query": "Best investments considering current market conditions?",
        "expected_intent": "news_invest"
    },

    {
        "query": "Given interest rate uncertainty where should I invest?",
        "expected_intent": "news_invest"
    },

    {
        "query": "What sectors benefit from AI boom?",
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
        "query": "Latest AI sector trends?",
        "expected_intent": "general_news"
    },

    {
        "query": "What are current inflation concerns globally?",
        "expected_intent": "general_news"
    },

    {
        "query": "How are global markets performing?",
        "expected_intent": "general_news"
    },

    {
        "query": "What is the latest economic outlook?",
        "expected_intent": "general_news"
    },

    # =================================================
# COMPLEX ALLOCATION
# =================================================

{
    "query": (
        "I am 32 years old with medium risk tolerance and want "
        "a diversified long-term portfolio for wealth creation."
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "How should I allocate investments across equity, debt, "
        "and gold for balanced growth?"
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "Suggest a portfolio strategy for someone looking "
        "for moderate risk and long-term appreciation."
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "I want exposure to Indian and US markets while keeping "
        "overall portfolio risk moderate."
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "Can you recommend a diversified investment allocation "
        "for financial independence over 20 years?"
    ),
    "expected_intent": "allocation"
},

# =================================================
# COMPLEX ADVICE
# =================================================

{
    "query": (
        "Markets seem highly uncertain right now and I am confused "
        "whether I should invest immediately or wait."
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "I want decent long-term returns but I really don't want "
        "to take excessive risk."
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "Given inflation concerns and economic slowdown fears, "
        "does it still make sense to invest aggressively?"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "I am worried about market crashes but also don't want "
        "my savings sitting idle."
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "What would be a sensible approach for someone who wants "
        "growth with reasonable safety?"
    ),
    "expected_intent": "advice"
},

# =================================================
# COMPLEX NEWS INVEST
# =================================================

{
    "query": (
        "Considering rising inflation and interest rates, "
        "where should I invest right now?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "Which sectors are likely to perform well given "
        "the current AI boom and market trends?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "What investments look attractive considering "
        "recession fears and global uncertainty?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "Given today's macroeconomic environment, "
        "which asset classes seem promising?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "How should investors position themselves during "
        "high inflation and market volatility?"
    ),
    "expected_intent": "news_invest"
},

# =================================================
# COMPLEX GENERAL NEWS
# =================================================

{
    "query": (
        "What are the latest developments impacting "
        "global financial markets?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "How are inflation and interest rate changes "
        "affecting global economies?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "What are analysts currently saying about "
        "technology sector trends?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "What is the current outlook for global equity markets?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "What major economic risks are investors "
        "currently discussing globally?"
    ),
    "expected_intent": "general_news"
},

# =================================================
# AMBIGUOUS / EDGE CASES
# =================================================

{
    "query": (
        "I want good returns but I also want safety. "
        "What should I do?"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "Can you suggest investments that are relatively safe "
        "but still beat inflation?"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "Given today's uncertainty, should investors focus "
        "more on equity or debt?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "What portfolio structure makes sense for long-term "
        "wealth creation with controlled risk?"
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "Markets are volatile and interest rates are rising. "
        "What is generally considered a sensible investment approach?"
    ),
    "expected_intent": "advice"
},

# =================================================
# NOISY / REALISTIC USER LANGUAGE
# =================================================

{
    "query": (
        "hmm markets kinda weird rn so idk where investing "
        "even makes sense anymore"
    ),
    "expected_intent": "advice"
},

{
    "query": (
        "thinking maybe something diversified and medium risk "
        "for long term growth?"
    ),
    "expected_intent": "allocation"
},

{
    "query": (
        "what sectors are people optimistic about currently?"
    ),
    "expected_intent": "general_news"
},

{
    "query": (
        "if inflation keeps rising where do investors usually move money?"
    ),
    "expected_intent": "news_invest"
},

{
    "query": (
        "i don't want super risky investments but savings accounts "
        "feel too slow"
    ),
    "expected_intent": "advice"
}
]


# =====================================================
# TEST RUNNER
# =====================================================

def run_remaining_intent_tests(
    detect_remaining_intent,
    state,
    llm
):

    correct = 0

    for i, case in enumerate(test_cases, 1):

        query = case["query"]
        expected = case["expected_intent"]

        predicted = detect_remaining_intent(
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

    from agents.advisor_agent import detect_remaining_intent

    run_remaining_intent_tests(
        detect_remaining_intent,
        state,
        llm
    )