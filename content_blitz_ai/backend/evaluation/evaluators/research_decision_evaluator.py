import json
import sys
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ============================================================
# PYTHON PATH
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from src.agents.research_decision_agent import research_decision_agent


# ============================================================
# DATASET
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "research_decision"
    / "research_decision_cases.json"
)


def load_cases():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# EVALUATE ONE CASE
# ============================================================

def evaluate_case(case):

    state = {
        "user_query": case["input"],
        "trace": [],
        "errors": [],
    }

    expected = case["expected"]["research_decision"]

    try:

        result = research_decision_agent(state)

        # IMPORTANT:
        # We need to determine the actual field used
        # by your research_decision_agent.
        requires_research = result.get(
        "requires_research"
            )       

        if requires_research is True:
            actual = "RESEARCH"

        elif requires_research is False:
            actual = "NO_RESEARCH"

        else:
            actual = None

        passed = actual == expected

        return {
            "id": case["id"],
            "input": case["input"],
            "category": case["category"],
            "priority": case.get("priority"),
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "error": None,
        }

    except Exception as e:

        return {
            "id": case["id"],
            "input": case["input"],
            "category": case["category"],
            "priority": case.get("priority"),
            "expected": expected,
            "actual": None,
            "passed": False,
            "error": repr(e),
        }


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation():

    cases = load_cases()

    results = [
        evaluate_case(case)
        for case in cases
    ]

    total = len(results)

    passed = sum(
        result["passed"]
        for result in results
    )

    failed = total - passed

    y_true = [
        result["expected"]
        for result in results
    ]

    y_pred = [
    result["actual"]
    if result["actual"] is not None
    else "ERROR"
    for result in results
    ]

    labels = sorted(
    {
        label
        for label in set(y_true) | set(y_pred)
        if label is not None
    }
    )

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "accuracy": accuracy,
        "classification_report": report,
        "labels": labels,
        "confusion_matrix": matrix,
        "results": results,
    }


# ============================================================
# PRINT REPORT
# ============================================================

def print_report(report):

    print("\n" + "=" * 70)
    print("RESEARCH DECISION EVALUATION")
    print("=" * 70)

    print(
        f"Total cases : {report['total_cases']}"
    )

    print(
        f"Passed      : {report['passed_cases']}"
    )

    print(
        f"Failed      : {report['failed_cases']}"
    )

    print(
        f"Accuracy    : {report['accuracy']:.2%}"
    )

    metrics = report["classification_report"]

    print("\n" + "-" * 70)
    print("OVERALL METRICS")
    print("-" * 70)

    print(
        f"Macro Precision    : "
        f"{metrics['macro avg']['precision']:.2%}"
    )

    print(
        f"Macro Recall       : "
        f"{metrics['macro avg']['recall']:.2%}"
    )

    print(
        f"Macro F1           : "
        f"{metrics['macro avg']['f1-score']:.2%}"
    )

    print(
        f"Weighted Precision : "
        f"{metrics['weighted avg']['precision']:.2%}"
    )

    print(
        f"Weighted Recall    : "
        f"{metrics['weighted avg']['recall']:.2%}"
    )

    print(
        f"Weighted F1        : "
        f"{metrics['weighted avg']['f1-score']:.2%}"
    )

    print("\n" + "-" * 70)
    print("PER-CLASS METRICS")
    print("-" * 70)

    print(
        f"{'Class':20}"
        f"{'Precision':12}"
        f"{'Recall':12}"
        f"{'F1':12}"
        f"{'Support':10}"
    )

    for label in report["labels"]:

        stats = metrics[str(label)]

        print(
            f"{str(label):20}"
            f"{stats['precision']:.2%}      "
            f"{stats['recall']:.2%}      "
            f"{stats['f1-score']:.2%}      "
            f"{stats['support']}"
        )

    print("\n" + "-" * 70)
    print("CONFUSION MATRIX")
    print("-" * 70)

    print(
        "Labels:",
        report["labels"]
    )

    print(
        report["confusion_matrix"]
    )

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

            print(
                f"\nID       : {result['id']}"
            )

            print(
                f"Category : {result['category']}"
            )

            print(
                f"Priority : {result['priority']}"
            )

            print(
                f"Input    : {result['input']!r}"
            )

            print(
                f"Expected : {result['expected']!r}"
            )

            print(
                f"Actual   : {result['actual']!r}"
            )

            print(
                f"Error    : {result['error']!r}"
            )

    print("\n" + "=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    report = run_evaluation()

    print_report(report)