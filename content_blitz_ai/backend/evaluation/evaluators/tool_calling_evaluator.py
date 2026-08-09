import json
import sys
from pathlib import Path
from unittest.mock import patch

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)


# ============================================================
# PATH SETUP
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# ============================================================
# IMPORT AGENTS
# ============================================================

from src.agents.blog_writer_agent import blog_writer_agent
from src.agents.linkedin_writer_agent import linkedin_writer_agent
from src.agents.image_agent import image_agent
from src.agents.research_agent import research_agent

# ============================================================
# DATASET
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "tool_calling"
    / "tool_call_cases.json"
)


def load_cases():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# MOCK LLM
# ============================================================

class FakeLLMResult:
    content = "Generated evaluation content."
    metadata = {}


class FakeLLMService:

    @staticmethod
    def invoke(*args, **kwargs):
        return FakeLLMResult()

    @staticmethod
    def stream(*args, **kwargs):
        yield "Generated "
        yield "evaluation "
        yield "content."


# ============================================================
# TOOL EXECUTION MOCK
# ============================================================

# ============================================================
# AGENT RUNNER
# ============================================================

def run_agent_for_case(case):

    agent_name = case["agent"]
    tool_input = case.get("input", {})

    if "topic" in tool_input:
        user_query = tool_input["topic"]

    elif "prompt" in tool_input:
        user_query = tool_input["prompt"]

    elif "query" in tool_input:
        user_query = tool_input["query"]

    else:
        user_query = "Evaluation test query"

    state = {
    "user_query": user_query,

    "current_intent": (
        "blog"
        if agent_name == "blog_writer_agent"
        else "linkedin"
        if agent_name == "linkedin_writer_agent"
        else "image"
    ),

    "content_plan": "Evaluation content plan",
    "research_content": "",
    "conversation_history": [],
    "retrieved_memories": [],
    "trace": [],
    "errors": [],
    }

    expected_operation = case["operation"]
    expected_tool = case["expected_tool"]
    
    try:

        if agent_name == "blog_writer_agent":

            with patch(
                "src.agents.blog_writer_agent.LLMService",
                FakeLLMService,
            ):
                result = blog_writer_agent(state)

        elif agent_name == "linkedin_writer_agent":

        

            with patch(
                "src.agents.linkedin_writer_agent.LLMService",
                FakeLLMService,
                ):
                result = linkedin_writer_agent(state)

        elif agent_name == "image_agent":

            with patch(
                "src.tools.image_tools.generate_image",
                return_value="mocked_image_url",
            ):
                result = image_agent(state)

        elif agent_name == "research_agent":
            with patch(
            "src.agents.research_agent.LLMService",
            FakeLLMService,
            ):
                result = research_agent(state)

        else:
            if expected_tool == "NO_TOOL":
                return {
                "id": case["id"],
                "agent": agent_name,
                "operation": expected_operation,
                "expected_tool": expected_tool,
                "actual_tool": "NO_TOOL",
                "passed": True,
                "status": "success",
                "error": None,
                }

            return {
            "id": case["id"],
            "agent": agent_name,
            "operation": expected_operation,
            "expected_tool": expected_tool,
            "actual_tool": "NO_TOOL",
            "passed": False,
            "status": "failed",
            "error": f"Unsupported agent: {agent_name}",
            }

        tool_calls = [
            trace
            for trace in result.get("trace", [])
            if trace.get("action") == "tool_call"
        ]

        matching_calls = [
            trace
            for trace in tool_calls
            if trace.get("operation") == expected_operation
            ]

        if expected_tool == "NO_TOOL":
            actual_tool = (
                matching_calls[0].get("tool")
                if matching_calls
                else "NO_TOOL"
            )

            passed = actual_tool == "NO_TOOL"

            return {
            "id": case["id"],
            "agent": agent_name,
            "operation": expected_operation,
            "expected_tool": expected_tool,
            "actual_tool": actual_tool,
            "passed": passed,
            "status": "success" if passed else "failed",
            "error": None if passed else "Unexpected tool call",
            }

        if matching_calls:
            actual_tool = matching_calls[0].get("tool")

            passed = actual_tool == expected_tool

            return {
            "id": case["id"],
            "agent": agent_name,
            "operation": expected_operation,
            "expected_tool": expected_tool,
            "actual_tool": actual_tool,
            "passed": passed,
            "status": matching_calls[0].get("status"),
        "error": None,
        }

        return {
        "id": case["id"],
        "agent": agent_name,
        "operation": expected_operation,
        "expected_tool": expected_tool,
        "actual_tool": "NO_TOOL",
        "passed": False,
        "status": None,
        "error": "Expected operation was not found in trace",
        }   

    except Exception as e:

        return {
            "id": case["id"],
            "agent": agent_name,
            "operation": expected_operation,
            "expected_tool": case["expected_tool"],
            "actual_tool": "NO_TOOL",
            "passed": False,
            "status": "failed",
            "error": repr(e),
        }


# ============================================================
# EVALUATION
# ============================================================

def run_evaluation():

    cases = load_cases()

    results = [
        run_agent_for_case(case)
        for case in cases
    ]

    y_true = [
    result["expected_tool"]
    if result["expected_tool"] is not None
    else "NO_TOOL"
    for result in results
    ]   

    y_pred = [
    result["actual_tool"]
    if result["actual_tool"] is not None
    else "NO_TOOL"
    for result in results
    ]

    passed = [
        result["passed"]
        for result in results
    ]

    total = len(results)
    passed_count = sum(passed)
    failed_count = total - passed_count

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    labels = sorted(
        set(y_true) | set(y_pred)
    )

    precision, recall, f1, support = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
        )
    )

    macro_precision = precision.mean()
    macro_recall = recall.mean()
    macro_f1 = f1.mean()

    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=labels,
            average="weighted",
            zero_division=0,
        )
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    return {
        "total_cases": total,
        "passed_cases": passed_count,
        "failed_cases": failed_count,
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "labels": labels,
        "confusion_matrix": matrix,
        "results": results,
    }


# ============================================================
# REPORT
# ============================================================

def print_report(report):

    print("\n" + "=" * 70)
    print("TOOL CALLING EVALUATION")
    print("=" * 70)

    print(f"Total cases : {report['total_cases']}")
    print(f"Passed      : {report['passed_cases']}")
    print(f"Failed      : {report['failed_cases']}")
    print(f"Accuracy    : {report['accuracy']:.2%}")

    print("\n" + "-" * 70)
    print("OVERALL METRICS")
    print("-" * 70)

    print(
        f"Macro Precision    : "
        f"{report['macro_precision']:.2%}"
    )

    print(
        f"Macro Recall       : "
        f"{report['macro_recall']:.2%}"
    )

    print(
        f"Macro F1           : "
        f"{report['macro_f1']:.2%}"
    )

    print(
        f"Weighted Precision : "
        f"{report['weighted_precision']:.2%}"
    )

    print(
        f"Weighted Recall    : "
        f"{report['weighted_recall']:.2%}"
    )

    print(
        f"Weighted F1        : "
        f"{report['weighted_f1']:.2%}"
    )

    print("\n" + "-" * 70)
    print("PER-TOOL METRICS")
    print("-" * 70)

    labels = report["labels"]
    matrix = report["confusion_matrix"]

    for index, label in enumerate(labels):

        row_total = matrix[index].sum()
        true_positive = matrix[index][index]

        column_total = matrix[:, index].sum()

        precision = (
            true_positive / column_total
            if column_total
            else 0
        )

        recall = (
            true_positive / row_total
            if row_total
            else 0
        )

        f1 = (
            2 * precision * recall /
            (precision + recall)
            if precision + recall
            else 0
        )

        print(
            f"{label:30} "
            f"{precision:8.2%} "
            f"{recall:8.2%} "
            f"{f1:8.2%} "
            f"{row_total:8}"
        )

    print("\n" + "-" * 70)
    print("CONFUSION MATRIX")
    print("-" * 70)

    print("Labels:", report["labels"])

    for row in report["confusion_matrix"]:
        print(list(row))

    print("\n" + "-" * 70)
    print("FAILURES")
    print("-" * 70)

    failures = [
        result
        for result in report["results"]
        if not result["passed"]
    ]

    if not failures:

        print("No failures.")

    else:

        for result in failures:

            print(f"\nID            : {result['id']}")
            print(f"Agent         : {result['agent']}")
            print(f"Operation     : {result['operation']}")
            print(
                f"Expected Tool : "
                f"{result['expected_tool']!r}"
            )
            print(
                f"Actual Tool   : "
                f"{result['actual_tool']!r}"
            )
            print(
                f"Status        : "
                f"{result.get('status')!r}"
            )
            print(
                f"Error         : "
                f"{result.get('error')!r}"
            )

    print("\n" + "=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    report = run_evaluation()

    print_report(report)