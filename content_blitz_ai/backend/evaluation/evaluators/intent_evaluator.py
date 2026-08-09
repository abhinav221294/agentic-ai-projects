import json
from pathlib import Path
import sys
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.agents.query_handler import query_handler


DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "intent"
    / "intent_cases.json"
)
def load_cases():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def evaluate_case(case):

    state = {
        "user_query": case["input"],
        "trace": [],
        "errors": [],
    }

    expected = case["expected"]["intent"]

    try:

        result = query_handler(state)

        actual = result.get(
            "current_intent",
            None
        )

        passed = actual == expected

        return {
            "id": case["id"],
            "input": case["input"],
            "category": case["category"],
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
            "expected": expected,
            "actual": None,
            "passed": False,
            "error": repr(e),
        }


def calculate_metrics(results):

    y_true = [
        result["expected"]
        for result in results
    ]

    y_pred = [
        result["actual"]
        if result["actual"] is not None
        else "__ERROR__"
        for result in results
    ]

    labels = sorted(
        set(y_true) | set(y_pred)
    )

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    classification = classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    return {
        "accuracy": accuracy,

        "macro_precision":
            classification["macro avg"]["precision"],

        "macro_recall":
            classification["macro avg"]["recall"],

        "macro_f1":
            classification["macro avg"]["f1-score"],

        "weighted_precision":
            classification["weighted avg"]["precision"],

        "weighted_recall":
            classification["weighted avg"]["recall"],

        "weighted_f1":
            classification["weighted avg"]["f1-score"],

        "per_class": {
            label: {
                "precision":
                    classification[label]["precision"],
                "recall":
                    classification[label]["recall"],
                "f1":
                    classification[label]["f1-score"],
                "support":
                    classification[label]["support"],
            }
            for label in labels
        },

        "labels": labels,

        "confusion_matrix":
            matrix.tolist(),
    }


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

    metrics = calculate_metrics(
        results
    )

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "metrics": metrics,
        "results": results,
    }


def print_report(report):

    metrics = report["metrics"]

    print("\n" + "=" * 70)
    print("INTENT CLASSIFICATION EVALUATION")
    print("=" * 70)

    print(
        f"Total cases : "
        f"{report['total_cases']}"
    )

    print(
        f"Passed      : "
        f"{report['passed_cases']}"
    )

    print(
        f"Failed      : "
        f"{report['failed_cases']}"
    )

    print("\n" + "-" * 70)
    print("OVERALL METRICS")
    print("-" * 70)

    print(
        f"Accuracy           : "
        f"{metrics['accuracy']:.2%}"
    )

    print(
        f"Macro Precision    : "
        f"{metrics['macro_precision']:.2%}"
    )

    print(
        f"Macro Recall       : "
        f"{metrics['macro_recall']:.2%}"
    )

    print(
        f"Macro F1           : "
        f"{metrics['macro_f1']:.2%}"
    )

    print(
        f"Weighted Precision : "
        f"{metrics['weighted_precision']:.2%}"
    )

    print(
        f"Weighted Recall    : "
        f"{metrics['weighted_recall']:.2%}"
    )

    print(
        f"Weighted F1        : "
        f"{metrics['weighted_f1']:.2%}"
    )

    print("\n" + "-" * 70)
    print("PER-CLASS METRICS")
    print("-" * 70)

    print(
        f"{'Class':15}"
        f"{'Precision':12}"
        f"{'Recall':12}"
        f"{'F1':12}"
        f"{'Support':10}"
    )

    for label, values in (
        metrics["per_class"].items()
    ):

        print(
            f"{label:15}"
            f"{values['precision']:.2%}      "
            f"{values['recall']:.2%}      "
            f"{values['f1']:.2%}      "
            f"{values['support']}"
        )

    print("\n" + "-" * 70)
    print("CONFUSION MATRIX")
    print("-" * 70)

    print(
        "Labels:",
        metrics["labels"],
    )

    for row in metrics["confusion_matrix"]:
        print(row)

    failures = [
        result
        for result in report["results"]
        if not result["passed"]
    ]

    print("\n" + "-" * 70)
    print("FAILURES")
    print("-" * 70)

    if not failures:

        print("No failures.")

    else:

        for result in failures:

            print(
                f"\nID       : "
                f"{result['id']}"
            )

            print(
                f"Category : "
                f"{result['category']}"
            )

            print(
                f"Input    : "
                f"{result['input']!r}"
            )

            print(
                f"Expected : "
                f"{result['expected']!r}"
            )

            print(
                f"Actual   : "
                f"{result['actual']!r}"
            )

            print(
                f"Error    : "
                f"{result['error']!r}"
            )

    print("\n" + "=" * 70)


if __name__ == "__main__":

    report = run_evaluation()

    print_report(report)