import json
import sys
from pathlib import Path
from unittest.mock import patch

# ============================================================
# PATH SETUP
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# ============================================================
# IMPORT
# ============================================================

from src.agents.research_agent import research_agent


# ============================================================
# DATASET
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "research"
    / "research_quality_cases.json"
)


def load_cases():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# MOCK LLM
# ============================================================

class FakeLLMResult:

    content = "Generated research result."
    metadata = {}


class FakeLLMService:

    @staticmethod
    def invoke(*args, **kwargs):
        return FakeLLMResult()

    @staticmethod
    def stream(*args, **kwargs):
        yield "Generated "
        yield "research "
        yield "result."


# ============================================================
# MOCK WEB SEARCH TOOL
# ============================================================

class FakeSearchTool:

    name = "web_search_tool"

    def invoke(self, tool_input):

        query = tool_input.get("query", "")

        return {
            "results": [
                {
                    "title": f"Research result for {query}",
                    "content": (
                        f"Research information related to {query}."
                    ),
                    "citations": [
                        "https://example.com/research"
                    ],
                }
            ]
        }


# ============================================================
# RUN CASE
# ============================================================

def run_case(case):

    expected = case.get("expected", {})
    query = case.get("query", "")

    state = {
        "user_query": query,
        "current_intent": "research",
        "content_plan": "Evaluation content plan",
        "research_content": "",
        "conversation_history": [],
        "retrieved_memories": [],
        "trace": [],
        "errors": [],
    }

    try:

        with patch(
            "src.agents.research_agent.LLMService",
            FakeLLMService,
        ), patch(
            "src.agents.research_agent.web_search_tool",
            FakeSearchTool(),
        ):

            result = research_agent(state)

        trace = result.get("trace", [])

        tool_calls = [
            entry
            for entry in trace
            if entry.get("action") == "tool_call"
        ]

        web_search_calls = [
            entry
            for entry in tool_calls
            if entry.get("tool") == "web_search_tool"
        ]

        synthesis_completed = any(
            entry.get("action") == "synthesis_completed"
            for entry in trace
        )

        research_completed = any(
            entry.get("action") == "research_completed"
            for entry in trace
        )

        # ----------------------------------------------------
        # Evaluate retrieval
        # ----------------------------------------------------

        retrieval_ok = len(web_search_calls) > 0

        # ----------------------------------------------------
        # Evaluate synthesis grounding
        # ----------------------------------------------------

        synthesis_ok = (
            synthesis_completed
            and bool(result.get("research_content"))
        )

        # ----------------------------------------------------
        # Freshness requirement
        # ----------------------------------------------------

        freshness_ok = True

        if expected.get("fresh_sources_required"):
            freshness_ok = retrieval_ok

        # ----------------------------------------------------
        # Overall case result
        # ----------------------------------------------------

        passed = (
            retrieval_ok
            and synthesis_ok
            and freshness_ok
            and research_completed
        )

        return {
            "id": case["id"],
            "query": query,
            "category": case.get("category"),
            "passed": passed,
            "retrieval": retrieval_ok,
            "synthesis": synthesis_ok,
            "freshness": freshness_ok,
            "expected": expected,
            "error": result.get("errors", []),
        }

    except Exception as e:

        return {
            "id": case["id"],
            "query": query,
            "category": case.get("category"),
            "passed": False,
            "retrieval": False,
            "synthesis": False,
            "freshness": False,
            "expected": expected,
            "error": str(e),
        }


# ============================================================
# EVALUATION
# ============================================================

def run_evaluation():

    cases = load_cases()

    results = [
        run_case(case)
        for case in cases
    ]

    passed = sum(
        result["passed"]
        for result in results
    )

    failed = len(results) - passed

    accuracy = (
        passed / len(results)
        if results
        else 0
    )

    print("\n==========================================")
    print("RESEARCH QUALITY EVALUATION")
    print("==========================================")

    print(f"\nTotal cases : {len(results)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Accuracy    : {accuracy:.2%}")

    print("\n--- CASE RESULTS ---")

    for result in results:

        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{result['id']:10} "
            f"{status:6} "
            f"{result['category']}"
        )

        if not result["passed"]:
            print(
                f"    Retrieval : {result['retrieval']}"
            )
            print(
                f"    Synthesis : {result['synthesis']}"
            )
            print(
                f"    Freshness : {result['freshness']}"
            )
            print(
                f"    Error     : {result['error']}"
            )

    print("\n--- SUMMARY ---")

    retrieval_pass = sum(
        result["retrieval"]
        for result in results
    )

    synthesis_pass = sum(
        result["synthesis"]
        for result in results
    )

    freshness_cases = [
        result
        for result in results
        if result["expected"].get("fresh_sources_required")
    ]

    freshness_pass = sum(
        result["freshness"]
        for result in freshness_cases
    )

    print(
        f"Retrieval Success : "
        f"{retrieval_pass}/{len(results)}"
    )

    print(
        f"Synthesis Success : "
        f"{synthesis_pass}/{len(results)}"
    )

    if freshness_cases:
        print(
            f"Freshness Checks  : "
            f"{freshness_pass}/{len(freshness_cases)}"
        )

    print("\n==========================================")

    return results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_evaluation()