from agents.router_agent import router_agent

results = []


def run_test(query, memory=None):
    state = {
        "query": query,
        "memory": memory or []
    }

    result = router_agent(state)
    actual = result.get("category")

    status = "✅ PASS" if actual == "advisor" else "❌ FAIL"

    print(status)
    print(f"Query: {query}")
    print(f"Category: {actual} (expected: advisor)")
    print("-" * 60)

    results.append(actual)


# =========================
# TEST SUITE (ADVISOR ONLY)
# =========================

def run_all_tests():

    # -------------------------
    # DIRECT ADVISOR
    # -------------------------
    print("\n===== DIRECT =====")

    run_test("Where should I invest?")
    run_test("Best investment option?")
    run_test("Should I invest in SIP?")
    run_test("Is crypto a good investment?")
    run_test("What should I do with my money?")

    # -------------------------
    # IMPLICIT ADVISOR
    # -------------------------
    print("\n===== IMPLICIT =====")
    run_test("portfolio not performing")
    run_test("not getting good returns")
    run_test("need better returns")
    run_test("want higher returns")

    # -------------------------
    # MIXED INTENT
    # -------------------------
    print("\n===== MIXED =====")

    run_test("What is SIP and should I invest?")
    run_test("Crypto is risky but should I invest?")
    run_test("TCS price is high should I buy?")
    run_test("Latest news is bad should I sell?")
    run_test("Explain mutual funds and suggest one")

    # -------------------------
    # RISK + DECISION
    # -------------------------
    print("\n===== RISK + DECISION =====")

    run_test("Is crypto risky and should I invest?")
    run_test("Are bonds safe and should I buy?")
    run_test("Mutual funds are risky should I avoid?")
    run_test("Is SIP safe and should I start?")

    # -------------------------
    # MARKET + DECISION
    # -------------------------
    print("\n===== MARKET + DECISION =====")

    run_test("TCS price high should I invest?")
    run_test("Stock market is down should I buy?")
    run_test("Reliance looks expensive should I wait?")
    run_test("Tesla stock is high should I invest?")

    # -------------------------
    # NEWS + DECISION
    # -------------------------
    print("\n===== NEWS + DECISION =====")

    run_test("Market news is negative should I invest?")
    run_test("Crypto news looks bad should I sell?")
    run_test("Recession news what should I do?")
    run_test("Latest updates suggest slowdown should I change investment?")

    # -------------------------
    # FOLLOW-UP (MEMORY)
    # -------------------------
    print("\n===== MEMORY =====")

    mem = [{"user": "What is SIP?", "assistant": "SIP explanation"}]
    run_test("Is it good?", memory=mem)

    mem2 = [{"user": "I invested in crypto", "assistant": "noted"}]
    run_test("Should I continue or exit?", memory=mem2)

    # -------------------------
    # WEAK / SHORT
    # -------------------------
    print("\n===== WEAK =====")

    run_test("invest now?")
    run_test("buy or wait?")
    run_test("safe option?")
    run_test("best option?")

    # -------------------------
    # REAL USER (ENGLISH ONLY)
    # -------------------------
    print("\n===== REAL USER =====")

    run_test("where should I invest my money")
    run_test("please help I am not getting good returns")
    run_test("crypto is falling what should I do")
    run_test("what should I invest in")
    run_test("need help choosing investment")

    # -------------------------
    # COMPLEX REAL WORLD
    # -------------------------
    print("\n===== COMPLEX =====")

    run_test("Market is crashing should I exit?")
    run_test("Interest rates rising where should I invest?")
    run_test("Crypto falling and risky what should I do?")
    run_test("Explain inflation and suggest investment")
    run_test("Gold vs mutual fund vs FD what should I choose?")
    run_test("Given current market conditions what should be my strategy?")


# =========================
# METRICS
# =========================

def accuracy():
    correct = sum(1 for r in results if r == "advisor")
    total = len(results)
    print(f"\n🎯 Advisor Routing Accuracy: {correct}/{total} ({(correct/total)*100:.2f}%)")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    run_all_tests()
    accuracy()