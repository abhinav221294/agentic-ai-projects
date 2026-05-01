from agents.router_agent import router_agent

results = []


def run_test(query, expected, memory=None):
    state = {
        "query": query,
        "memory": memory or []
    }

    result = router_agent(state)
    actual = result.get("category")

    results.append((expected, actual))

    status = "✅ PASS" if actual == expected else "❌ FAIL"

    print(status)
    print(f"{query} → {actual} (expected: {expected})")
    print("-" * 50)


def run_all_tests():

    # =========================
    # BASIC (RAG)
    # =========================
    print("\n===== RAG =====")
    run_test("What is SIP?", "rag")
    run_test("Explain mutual funds", "rag")
    run_test("Define NAV", "rag")
    run_test("What is index fund?", "rag")
    run_test("risk?", "rag")

    # =========================
    # NON-FINANCE
    # =========================
    print("\n===== NON-FINANCE =====")
    run_test("What is cricket?", "none")
    run_test("Explain football", "none")
    run_test("weather today", "none")
    run_test("movie recommendation", "none")

    # =========================
    # ADVISOR
    # =========================
    print("\n===== ADVISOR =====")
    run_test("Where should I invest money?", "advisor")
    run_test("Suggest portfolio for long term", "advisor")
    run_test("I want good returns", "advisor")
    run_test("Best mutual fund", "advisor")

    # =========================
    # MARKET
    # =========================
    print("\n===== MARKET =====")
    run_test("TCS price", "market")
    run_test("What is price of Tesla?", "market")
    run_test("latest price of TCS", "market")
    run_test("tcs latest price pls", "market")

    # =========================
    # NEWS
    # =========================
    print("\n===== NEWS =====")
    run_test("Latest news", "news")
    run_test("Market news today", "news")
    run_test("tcs latest news", "news")
    run_test("latest update on SIP", "news")

    # =========================
    # RISK
    # =========================
    print("\n===== RISK =====")
    run_test("Is crypto risky?", "risk")
    run_test("Are bonds safe?", "risk")
    run_test("crypto safe or not?", "risk")
    run_test("bond returns safe?", "risk")

    # =========================
    # COMPLEX (MULTI INTENT)
    # =========================
    print("\n===== COMPLEX =====")
    run_test("Is TCS a good investment?", "advisor")
    run_test("Should I invest in crypto?", "advisor")
    run_test("What is SIP and is it good?", "advisor")
    run_test("What is SIP and how to invest?", "advisor")
    run_test("Explain mutual funds and suggest one", "advisor")

    # =========================
    # AMBIGUOUS
    # =========================
    print("\n===== AMBIGUOUS =====")
    run_test("Tell me about SIP", "rag")
    run_test("SIP details", "rag")
    run_test("SIP investment plan", "rag")
    run_test("Mutual fund vs FD", "rag")

    # =========================
    # WEAK SIGNAL
    # =========================
    print("\n===== WEAK SIGNAL =====")
    run_test("SIP", "rag")
    run_test("crypto", "rag")

    # =========================
    # NOISY / REAL USER
    # =========================
    print("\n===== NOISE =====")
    run_test("hey bro what is sip", "rag")
    run_test("pls suggest good investment", "advisor")

    # =========================
    # SYMBOL EDGE
    # =========================
    print("\n===== SYMBOL =====")
    run_test("price of reliance", "market")
    run_test("reliance news", "news")
    run_test("is reliance good", "advisor")
    run_test("is reliance risky", "risk")

    # =========================
    # TRICKY CASES (FIXED)
    # =========================
    print("\n===== TRICKY =====")
    run_test("what is a good mutual fund?", "advisor")
    run_test("which mutual fund is good?", "advisor")
    run_test("risk of mutual funds explained", "rag")

    # =========================
    # CASE / PUNCTUATION
    # =========================
    print("\n===== CASE =====")
    run_test("WHAT IS SIP???", "rag")
    run_test("Is Crypto Risky!!!", "risk")
    run_test("tcs PRICE now", "market")

    # =========================
    # MEMORY TESTS
    # =========================
    print("\n===== MEMORY =====")

    mem1 = [{"user": "What is SIP?", "assistant": "SIP explanation"}]
    run_test("Is it good?", "advisor", mem1)

    mem2 = [{"user": "Is crypto risky?", "assistant": "Yes volatile"}]
    run_test("Should I invest?", "advisor", mem2)

    mem3 = [{"user": "TCS price", "assistant": "₹3500"}]
    run_test("Is it good?", "advisor", mem3)

    # =========================
    # 🔥 VERY COMPLEX (REAL WORLD)
    # =========================
    print("\n===== VERY COMPLEX =====")

    run_test("What is SIP and should I start one if market is down right now?", "advisor")
    run_test("Crypto is risky but should I invest for long term?", "advisor")
    run_test("Market is crashing today, should I exit my investments?", "advisor")
    run_test("Interest rates rising, where should I invest now?", "advisor")
    run_test("Explain inflation and tell me where to invest", "advisor")

    # =========================
    # 🔥 CONFLICT CASES
    # =========================
    print("\n===== CONFLICT =====")

    run_test("TCS price and should I invest?", "advisor")
    run_test("Latest news on crypto and should I buy?", "advisor")
    run_test("Is gold safe and should I invest?", "advisor")

    # =========================
    # 🔥 MISLEADING KEYWORDS
    # =========================
    print("\n===== MISLEADING =====")

    run_test("market is down meaning", "rag")
    run_test("risk meaning in finance", "rag")
    run_test("price meaning in stock market", "rag")

    # =========================
    # 🔥 IMPLICIT ADVISOR
    # =========================
    print("\n===== IMPLICIT ADVISOR =====")

    run_test("not getting good returns", "advisor")
    run_test("portfolio not performing well", "advisor")
    run_test("returns are low lately what to do", "advisor")

    # =========================
    # 🔥 ULTRA SHORT (HARD)
    # =========================
    print("\n===== ULTRA SHORT =====")

    run_test("invest now?", "advisor")
    run_test("buy or wait?", "advisor")
    run_test("safe option?", "advisor")

    # =========================
    # 🔥 LLM FAIL CASES
    # =========================
    print("\n===== LLM FAIL CASES =====")

    run_test("What is SIP?", "rag")
    run_test("Explain SIP and suggest plan", "advisor")
    run_test("crypto safe?", "risk")


# =========================
# METRICS
# =========================

def calculate_metrics(target_class):
    TP = FP = FN = 0

    for expected, actual in results:
        if actual == target_class and expected == target_class:
            TP += 1
        elif actual == target_class and expected != target_class:
            FP += 1
        elif actual != target_class and expected == target_class:
            FN += 1

    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0

    print(f"\n📊 {target_class.upper()}")
    print(f"TP={TP}, FP={FP}, FN={FN}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall   : {recall:.2f}")


def accuracy():
    correct = sum(1 for e, a in results if e == a)
    total = len(results)
    print(f"\n🎯 Accuracy: {correct}/{total} ({(correct/total)*100:.2f}%)")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    run_all_tests()

    accuracy()

    for cls in ["advisor", "rag", "news", "risk", "market", "none"]:
        calculate_metrics(cls)