from agents.rag_agent import rag_agent

results = []


def run_test(query, expect_source=True):
    state = {
        "query": query,
        "memory": []
    }

    result = rag_agent(state)

    answer = result.get("answer", "")
    sources = result.get("source", [])
    confidence = result.get("confidence")

    # -------------------------
    # VALIDATION
    # -------------------------
    has_source = len(sources) > 0

    status = "✅ PASS"

    if expect_source and not has_source:
        status = "❌ FAIL"

    if not expect_source and has_source:
        status = "❌ FAIL"

    print(status)
    print(f"Query: {query}")
    print(f"Confidence: {confidence}")
    print(f"Sources: {sources}")
    print(f"Answer: {answer[:120]}...")
    print("-" * 60)

    results.append((expect_source, has_source))


# =========================
# TEST SUITE
# =========================

def run_all_tests():

    # -------------------------
    # BASIC DEFINITIONS
    # -------------------------
    print("\n===== BASIC =====")

    run_test("What is SIP?")
    run_test("Explain mutual funds")
    run_test("What is diversification?")
    run_test("What is inflation?")

    # -------------------------
    # INTERMEDIATE
    # -------------------------
    print("\n===== INTERMEDIATE =====")

    run_test("How does SIP work?")
    run_test("Benefits of mutual funds")
    run_test("Types of investment risks")
    run_test("How inflation affects investment")

    # -------------------------
    # COMPLEX (MULTI-CONTEXT)
    # -------------------------
    print("\n===== COMPLEX =====")

    run_test("Difference between SIP and lump sum")
    run_test("Mutual funds vs stocks")
    run_test("Impact of inflation on returns")
    run_test("How diversification reduces risk")

    # -------------------------
    # MEMORY BASED
    # -------------------------
    print("\n===== MEMORY =====")

    mem = [{"user": "What is SIP?", "assistant": "SIP explanation"}]
    run_test("How is it different from lump sum?", expect_source=True)

    # -------------------------
    # EDGE CASES
    # -------------------------
    print("\n===== EDGE =====")

    run_test("random unknown finance term xyz", expect_source=False)
    run_test("asdfghjkl", expect_source=False)

    # -------------------------
    # SHORT QUERIES
    # -------------------------
    print("\n===== SHORT =====")

    run_test("sip")
    run_test("inflation")
    run_test("mutual fund")

    # -------------------------
    # REAL USER STYLE
    # -------------------------
    print("\n===== REAL USER =====")

    run_test("tell me about sip investment")
    run_test("how mutual funds work")
    run_test("explain risk in investment")
    run_test("what inflation means in simple terms")


# =========================
# METRICS
# =========================

def accuracy():
    correct = sum(1 for exp, act in results if exp == act)
    total = len(results)
    print(f"\n🎯 RAG Accuracy: {correct}/{total} ({(correct/total)*100:.2f}%)")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    run_all_tests()
    accuracy()