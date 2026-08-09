import json
from pathlib import Path


# ============================================================
# PATH SETUP
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "llm_output"
    / "llm_output_cases.json"
)


# ============================================================
# LOAD DATASET
# ============================================================

def load_cases():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# OUTPUT VALIDATION
# ============================================================

def validate_output(case):
    task = case["task"]
    output = case["output"]

    # --------------------------------------------------------
    # Research decision
    # --------------------------------------------------------

    if task == "research_decision":

        normalized = output.strip().upper()

        if normalized in {"RESEARCH", "NO_RESEARCH"}:
            return True

        return False

    # --------------------------------------------------------
    # Intent classification
    # --------------------------------------------------------

    if task == "intent_classification":

        normalized = output.strip().lower()

        # Exact value only.
        if normalized in {
            "blog",
            "linkedin",
            "image",
        }:
            return True

        return False

    # --------------------------------------------------------
    # Strategy generation
    # --------------------------------------------------------

    if task == "strategy_generation":

        try:
            parsed = json.loads(output)

            if isinstance(parsed, dict):
                return True

            return False

        except (json.JSONDecodeError, TypeError):
            return False

    # --------------------------------------------------------
    # Content generation
    # --------------------------------------------------------

    if task == "content_generation":

        return bool(output.strip())

    # --------------------------------------------------------
    # Unknown task
    # --------------------------------------------------------

    return False


# ============================================================
# EXPECTED RESULT
# ============================================================

def expected_result(case):
    expected = case["expected"]

    if expected in {
        "valid",
        "valid_after_normalization",
        "valid_json",
        "minimal_valid",
    }:
        return True

    if expected in {
        "invalid",
        "invalid_json",
        "invalid_or_needs_parsing",
    }:
        return False

    return False


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation():

    cases = load_cases()

    passed = 0
    failed = 0

    results = []

    for case in cases:

        actual = validate_output(case)
        expected = expected_result(case)

        is_pass = actual == expected

        if is_pass:
            passed += 1
        else:
            failed += 1

        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "expected": expected,
                "actual": actual,
                "status": "PASS" if is_pass else "FAIL",
            }
        )

    total = len(cases)
    accuracy = (passed / total * 100) if total else 0

    print("\n==========================================")
    print("LLM OUTPUT EVALUATION")
    print("==========================================")

    print(f"\nTotal cases : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Accuracy    : {accuracy:.2f}%")

    print("\n--- CASE RESULTS ---")

    for result in results:
        print(
            f"{result['id']:<10} "
            f"{result['status']:<6} "
            f"{result['category']}"
        )

    print("\n==========================================")

    return results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_evaluation()