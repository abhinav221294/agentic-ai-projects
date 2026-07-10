from evaluation.test_cases import TEST_CASES
from evaluation.evaluator import evaluate_response

import pandas as pd

results = []

for test in TEST_CASES:

    print("=" * 80)
    print(test["question"])

    df = evaluate_response(
        question=test["question"],
        answer=test["answer"],
        contexts=test["contexts"],
        ground_truth=test["ground_truth"]
    )

    print(df)

    results.append(df)

final_df = pd.concat(results, ignore_index=True)

final_df.to_csv(
    "evaluation/results.csv",
    index=False
)

print("\nEvaluation Complete")