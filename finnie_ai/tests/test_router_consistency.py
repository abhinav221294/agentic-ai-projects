from agents.router_agent import router_agent
from utils.state import AgentState
import random

# -------------------------
# PERTURBATION GENERATOR
# -------------------------

def generate_variations(query):
    variations = set()

    # Original
    variations.add(query)

    # Lower / upper
    variations.add(query.lower())
    variations.add(query.upper())

    # Add noise words
    noise_prefix = ["hey", "bro", "pls", "yo", "tell me"]
    noise_suffix = ["pls", "now", "quickly", "asap"]

    for p in noise_prefix:
        variations.add(f"{p} {query}")

    for s in noise_suffix:
        variations.add(f"{query} {s}")

    # Add punctuation
    variations.add(query + "?")
    variations.add(query + "!!!")

    # Replace common words
    replacements = {
        "invest": ["put money", "start investing"],
        "safe": ["secure", "low risk"],
        "good": ["worth it", "beneficial"],
        "price": ["value", "rate"]
    }

    for word, reps in replacements.items():
        if word in query.lower():
            for r in reps:
                variations.add(query.lower().replace(word, r))

    return list(variations)


# -------------------------
# RUN ROUTER
# -------------------------

def run_query(query):
    state: AgentState = {
        "query": query,
        "memory": [],
        "profile": {},
        "stage": None
    }
    result = router_agent(state)
    return result["category"]


# -------------------------
# ROBUSTNESS TEST
# -------------------------

def test_robustness(base_queries):
    print("\n===== ROBUSTNESS TEST =====\n")

    total = 0
    stable = 0

    for base in base_queries:
        variations = generate_variations(base)

        outputs = [run_query(q) for q in variations]
        unique = set(outputs)

        print(f"\nBase Query: {base}")
        print(f"Variations: {len(variations)}")
        print(f"Outputs: {outputs}")
        print(f"Unique: {unique}")

        total += 1

        if len(unique) == 1:
            print("✅ STABLE")
            stable += 1
        else:
            print("❌ UNSTABLE")

    print("\n===================================")
    print(f"Stability Score: {stable}/{total}")
    print(f"Percentage: {round(stable/total*100, 2)}%")
    print("===================================")


# -------------------------
# TEST SET
# -------------------------

if __name__ == "__main__":
    base_queries = [
        "Should I invest",
        "safe option",
        "What is SIP",
        "crypto risky",
        "Mutual fund vs FD",
        "not getting good returns",
        "TCS price",
        "Is it good"
    ]

    test_robustness(base_queries)