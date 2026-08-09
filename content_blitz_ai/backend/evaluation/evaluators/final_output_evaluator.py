import json
import sys
from pathlib import Path

# ============================================================
# PATH SETUP
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.core.config import (
    EVALUATION_LLM_MODEL,
    EVALUATION_LLM_TEMPERATURE,
    EVALUATION_LLM_MAX_TOKENS,
)
from src.integrations.gemini_client import gemini_llm_client





# ============================================================
# DATASET
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "content"
    / "content_quality_cases.json"
)


def load_cases():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# EVALUATION LLM
# ============================================================

def get_evaluation_llm():

    return gemini_llm_client(
        model=EVALUATION_LLM_MODEL,
        temperature=EVALUATION_LLM_TEMPERATURE,
        max_tokens=EVALUATION_LLM_MAX_TOKENS,
    )


# ============================================================
# LLM JUDGE
# ============================================================

def evaluate_output(
    llm,
    case,
    output,
):

    criteria = case["criteria"]

    criteria_text = "\n".join(
        f"- {criterion}"
        for criterion in criteria
    )

    prompt = f"""You are evaluating the quality of an AI-generated content output.

USER REQUEST:
{case["input"]}

CONTENT TYPE:
{case["type"]}

GENERATED OUTPUT:
{output}

EVALUATION CRITERIA:
{criteria_text}

Score EVERY criterion from 1 to 5:
1=Very poor, 2=Poor, 3=Acceptable, 4=Good, 5=Excellent.

Evaluate ONLY the criteria provided above.
Keep the reason under 30 words.

Return ONLY valid JSON:

{{
  "scores": {{
    "criterion_name": 1,
    "another_criterion": 5
  }},
  "overall_score": 3.5,
  "reason": "Brief explanation."
}}"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        content = " ".join(
            block.text
            for block in content
            if hasattr(block, "text")
        )

    content = str(content).strip()

    # Handle accidental markdown fences
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    return json.loads(content)


# ============================================================
# ACTUAL CONTENT GENERATION
# ============================================================

def generate_content(case):

    state = {
        "user_query": case["input"],
        "current_intent": case["type"],
        "content_plan": (
            "Generate high-quality content for the user's request."
        ),
        "research_content": "",
        "conversation_history": [],
        "retrieved_memories": [],
        "trace": [],
        "errors": [],
    }

    if case["type"] == "blog":

        from src.agents.blog_writer_agent import blog_writer_agent

        result = blog_writer_agent(state)

        return result.get("answer", "")

    if case["type"] == "linkedin":

        from src.agents.linkedin_writer_agent import (
            linkedin_writer_agent
        )

        result = linkedin_writer_agent(state)

        return result.get("answer", "")

    if case["type"] == "image":

        from src.agents.image_agent import image_agent

        result = image_agent(state)

        return result.get("image_prompt", "")

    raise ValueError(
        f"Unsupported content type: {case['type']}"
    )


# ============================================================
# RUN EVALUATION
# ============================================================

def run_evaluation():

    cases = load_cases()

    llm = get_evaluation_llm()

    results = []

    for case in cases:

        print(
            f"\n========== {case['id']} =========="
        )

        try:

            output = generate_content(case)

            evaluation = evaluate_output(
                llm=llm,
                case=case,
                output=output,
            )

            result = {
                "id": case["id"],
                "type": case["type"],
                "category": case["category"],
                "output": output,
                "scores": evaluation["scores"],
                "overall_score": evaluation["overall_score"],
                "reason": evaluation.get("reason", ""),
            }

            results.append(result)

            print(
                f"Overall Score : "
                f"{evaluation['overall_score']}/5"
            )

            print(
                f"Scores        : "
                f"{evaluation['scores']}"
            )

            print(
                f"Reason        : "
                f"{evaluation.get('reason', '')}"
            )

        except Exception as e:

            print(
                f"ERROR: {repr(e)}"
            )

            results.append(
                {
                    "id": case["id"],
                    "error": repr(e),
                }
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    scores = [
        r["overall_score"]
        for r in results
        if "overall_score" in r
    ]

    average_score = (
        sum(scores) / len(scores)
        if scores
        else None
    )

    print("\n==========================================")
    print("FINAL OUTPUT QUALITY EVALUATION")
    print("==========================================")

    print(
        f"\nTotal cases : {len(cases)}"
    )

    print(
        f"Evaluated   : {len(scores)}"
    )

    print(
        f"Average     : "
        f"{average_score:.2f}/5"
        if average_score is not None
        else "Average     : None"
    )

    print("\n--- CASE RESULTS ---")

    for result in results:

        if "overall_score" in result:

            print(
                f"{result['id']:<22}"
                f"{result['overall_score']:.2f}/5"
            )

        else:

            print(
                f"{result['id']:<22}"
                f"FAILED"
            )

    print("\n==========================================")

    return results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_evaluation()