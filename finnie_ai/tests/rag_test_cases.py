from rag_pipeline import RAGPipeline
import time

# -------------------------
# TEST CASES (expanded)
# -------------------------
TEST_QUERIES = [

    # -------- BASIC DEFINITIONS --------
    {
        "query": "What is a bond?",
        "expected_keywords": ["debt", "interest", "issuer"],
        "expected_source": "bond"
    },
    {
        "query": "What is NAV in mutual funds?",
        "expected_keywords": ["net asset value", "fund"],
        "expected_source": "nav"
    },

    # -------- PDF HEAVY --------
    {
        "query": "What is bond duration?",
        "expected_keywords": ["interest rate", "sensitivity"],
        "expected_source": "bond"
    },
    {
        "query": "Explain yield to maturity",
        "expected_keywords": ["yield", "return"],
        "expected_source": "bond"
    },

    # -------- COMPARISON --------
    {
        "query": "Difference between equity and debt",
        "expected_keywords": ["risk", "returns"],
        "expected_source": "stocks"
    },

    # -------- CONCEPTUAL --------
    {
        "query": "How does inflation affect investments?",
        "expected_keywords": ["purchasing power", "returns"],
        "expected_source": "inflation"
    },
    {
        "query": "What is diversification?",
        "expected_keywords": ["risk", "portfolio"],
        "expected_source": "diversification"
    },

    # -------- PRACTICAL --------
    {
        "query": "What are SIP benefits?",
        "expected_keywords": ["systematic", "investment"],
        "expected_source": "sip"
    },
    {
        "query": "What are risks in stock market?",
        "expected_keywords": ["volatility", "loss"],
        "expected_source": "risks"
    },

    # -------- EDGE CASE --------
    {
        "query": "safe investment options",
        "expected_keywords": ["low risk", "stable"],
        "expected_source": "debt"
    }
]


# -------------------------
# EVALUATION FUNCTION
# -------------------------
def evaluate_rag():

    rag = RAGPipeline()

    total_score = 0
    total_tests = len(TEST_QUERIES)

    print("\n🚀 Starting RAG Evaluation...\n")

    for i, test in enumerate(TEST_QUERIES, 1):

        query = test["query"]
        expected_keywords = test["expected_keywords"]
        expected_source = test["expected_source"]

        print("=" * 60)
        print(f"🧪 Test {i}: {query}")

        # -------------------------
        # LATENCY
        # -------------------------
        start = time.time()
        results = rag.retrieve(query)
        latency = round(time.time() - start, 2)

        if not results:
            print("❌ No results retrieved")
            continue

        retrieved_text = " ".join([r["content"].lower() for r in results])
        sources = [r["source_file_name"].lower() for r in results]

        # -------------------------
        # 1. RELEVANCE SCORE
        # -------------------------
        hits = sum(1 for word in expected_keywords if word in retrieved_text)
        relevance_score = hits / len(expected_keywords)

        # -------------------------
        # 2. SOURCE MATCH
        # -------------------------
        source_match = any(expected_source in s for s in sources)

        # -------------------------
        # 3. CONTEXT QUALITY
        # -------------------------
        context_quality = "GOOD" if relevance_score > 0.6 else "WEAK"

        # -------------------------
        # 4. RESPONSE GROUNDING
        # -------------------------
        answer_simulated = " ".join([r["content"][:200] for r in results])

        grounded_hits = sum(1 for word in expected_keywords if word in answer_simulated.lower())
        grounded_score = grounded_hits / len(expected_keywords)

        # -------------------------
        # 5. CONFIDENCE CHECK
        # -------------------------
        confidences = [r["confidence"] for r in results]
        avg_conf = sum(confidences) / len(confidences)

        # -------------------------
        # OUTPUT
        # -------------------------
        print(f"\n⏱ Latency: {latency}s")
        print(f"📊 Relevance Score: {relevance_score:.2f}")
        print(f"📂 Source Match: {source_match}")
        print(f"📈 Avg Confidence: {avg_conf:.2f}")
        print(f"🧠 Grounded Score: {grounded_score:.2f}")
        print(f"📄 Context Quality: {context_quality}")

        print("\n🔎 Sources Retrieved:")
        for s in sources:
            print(f"- {s}")

        print("\n📄 Top Chunk Preview:")
        print(results[0]["content"][:300])

        # -------------------------
        # FLAGS
        # -------------------------
        if relevance_score < 0.5:
            print("❌ Poor retrieval")

        if not source_match:
            print("⚠️ Wrong document retrieved")

        if grounded_score < 0.5:
            print("⚠️ Possible hallucination")

        if avg_conf < 0.5:
            print("⚠️ Low confidence retrieval")

        total_score += relevance_score

    # -------------------------
    # FINAL SUMMARY
    # -------------------------
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")

    avg_score = total_score / total_tests
    print(f"Overall Retrieval Score: {avg_score:.2f}")

    if avg_score > 0.75:
        print("✅ RAG Quality: GOOD")
    elif avg_score > 0.5:
        print("⚠️ RAG Quality: NEEDS IMPROVEMENT")
    else:
        print("❌ RAG Quality: POOR")

    print("=" * 60)


# -------------------------
# CONSISTENCY TEST
# -------------------------
def consistency_test():

    rag = RAGPipeline()

    queries = [
        "what is bond duration",
        "define bond duration",
        "bond duration meaning"
    ]

    print("\n🔁 Consistency Test\n")

    for q in queries:
        results = rag.retrieve(q)
        if results:
            print(f"{q} → {results[0]['source_file_name']}")
        else:
            print(f"{q} → No result")


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    evaluate_rag()
    consistency_test()