from utils.llm import get_llm
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =========================
# 💰 MODEL PRICING
# =========================

MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

# =========================
# 💰 COST CALCULATOR
# =========================

def calculate_cost(model, prompt_tokens, completion_tokens):
    pricing = MODEL_PRICING.get(model)

    if not pricing:
        raise ValueError(f"Pricing not defined for model: {model}")

    input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost


# =========================
# 🧪 TEST FUNCTION
# =========================

def test_llm(
    query,
    model="gpt-4o-mini",
    temperature=0.2,
    max_tokens=200,
    stage="test"
):
    llm = get_llm(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

    response = llm.invoke(query)

    # ⚠️ Extract token usage
    usage = response.response_metadata.get("token_usage", {})

    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    total_tokens = prompt_tokens + completion_tokens
    cost = calculate_cost(model, prompt_tokens, completion_tokens)

    print("\n==============================")
    print(f"Time: {datetime.now()}")
    print(f"Stage: {stage}")
    print(f"Model: {model}")
    print(f"Query: {query}")
    print(f"Response: {response.content}")
    print(f"Tokens: {prompt_tokens} (input) + {completion_tokens} (output)")
    print(f"Total Tokens: {total_tokens}")
    print(f"Cost: ${cost:.6f}")
    print("==============================\n")

    return cost


# =========================
# ▶️ RUN MULTIPLE TESTS
# =========================

if __name__ == "__main__":
    total_cost = 0

    test_cases = [
        {"query": "What is NAV?", "stage": "rag"},
        {"query": "Should I invest now?", "stage": "advisor"},
        {"query": "Explain inflation in simple terms", "stage": "rag"},
    ]

    for test in test_cases:
        cost = test_llm(
            query=test["query"],
            model="gpt-4o-mini",  # 🔁 change here
            temperature=0.3,
            max_tokens=200,
            stage=test["stage"]
        )

        total_cost += cost

    print(f"\n🔥 TOTAL COST: ${total_cost:.6f}")