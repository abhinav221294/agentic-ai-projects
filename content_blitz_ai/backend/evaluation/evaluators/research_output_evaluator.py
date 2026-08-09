import json
from pathlib import Path
from unittest.mock import patch
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[2]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.integrations.gemini_client import gemini_llm_client

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.config import (
    EVALUATION_LLM_MODEL,
    EVALUATION_LLM_MAX_TOKENS,
    EVALUATION_LLM_TEMPERATURE,
    EMBEDDING_MODEL,
)

from src.agents.research_agent import research_agent


# ============================================================
# PATH
# ============================================================

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "datasets"
    / "research"
    / "research_quality_cases.json"
)

# ============================================================
# LOAD DATASET
# ============================================================

def load_cases():

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# FAKE LLM
# ============================================================

class FakeLLMResult:

    content = (
        "Agentic AI is increasingly being used to build "
        "applications that can reason, use tools, and perform "
        "multi-step tasks."
    )

    metadata = {}


class FakeLLMService:

    @staticmethod
    def invoke(*args, **kwargs):
        return FakeLLMResult()


# ============================================================
# FAKE WEB SEARCH
# ============================================================

def fake_web_search(input_data):

    return {
        "results": [
            {
                "title": "Agentic AI Research Source",
                "content": (
                    "Agentic AI systems can reason, use tools, "
                    "and perform multi-step tasks."
                ),
                "citations": [
                    "https://example.com/source"
                ]
            }
        ]
    }


# ============================================================
# RUN RESEARCH AGENT
# ============================================================

def run_research_case(case):

    state = {
        "user_query": case["query"],
        "current_intent": "research",
        "content_plan": "Research evaluation",
        "research_content": "",
        "conversation_history": [],
        "retrieved_memories": [],
        "trace": [],
        "errors": [],
    }

    def fake_invoke_tool_with_trace(
        state,
        tool,
        tool_input,
        agent,
        operation,
    ):
        return fake_web_search(tool_input)

    with patch(
        "src.agents.research_agent.LLMService",
        FakeLLMService,
    ), patch(
        "src.agents.research_agent.invoke_tool_with_trace",
        side_effect=fake_invoke_tool_with_trace,
    ):

        result = research_agent(state)

    return result


# ============================================================
# EXTRACT CONTEXT
# ============================================================

def extract_contexts(result):

    research_data = result.get("research_data", {})

    contexts = []

    for item in research_data.get("results", []):

        content = item.get("content", "")

        if content:
            contexts.append(content)

    return contexts


# ============================================================
# RAGAS EVALUATION
# ============================================================

def run_ragas(query, answer, contexts):

    try:
        from ragas import SingleTurnSample
        from ragas.metrics import (
            Faithfulness,
            ResponseRelevancy,
        )

        # Evaluation LLM
        evaluator_llm = gemini_llm_client(
            model=EVALUATION_LLM_MODEL,
            temperature=EVALUATION_LLM_TEMPERATURE,
            max_tokens=EVALUATION_LLM_MAX_TOKENS,
        )

        ragas_llm = LangchainLLMWrapper(evaluator_llm)

        # Evaluation embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model=f"models/{EMBEDDING_MODEL}"
        )

        ragas_embeddings = LangchainEmbeddingsWrapper(
            embeddings
        )

        sample = SingleTurnSample( 
            user_input=query,
            response=answer,
            retrieved_contexts=contexts,
        )

        faithfulness_metric = Faithfulness(
            llm=ragas_llm
        )

        relevancy_metric = ResponseRelevancy(
            llm=ragas_llm,
            embeddings=ragas_embeddings,
        )

        faithfulness = faithfulness_metric.single_turn_score(
            sample
        )

        relevancy = relevancy_metric.single_turn_score(
            sample
        )

        return {
            "faithfulness": float(faithfulness),
            "answer_relevancy": float(relevancy),
        }

    except Exception as e:

        print("\n========== RAGAS ERROR ==========")
        print(repr(e))
        import traceback
        traceback.print_exc()
        print("=================================\n")

        return {
            "faithfulness": None,
            "answer_relevancy": None,
            "ragas_error": repr(e),
        }

# ============================================================
# SIMPLE LLM JUDGE
# ============================================================

def llm_judge(query, answer, contexts):

    context_text = "\n\n".join(contexts)

    prompt = f"""
You are an evaluator for a research agent.

Evaluate the answer using the retrieved context.

USER QUERY:
{query}

RETRIEVED CONTEXT:
{context_text}

ANSWER:
{answer}

Return ONLY valid JSON:

{{
    "relevance": 0.0,
    "groundedness": 0.0
}}

Scoring:
- relevance: How well the answer addresses the user query.
- groundedness: How well the answer is supported by the retrieved context.
- Scores must be between 0 and 1.
"""

    evaluator_llm = gemini_llm_client(
        model=EVALUATION_LLM_MODEL,
        temperature=0,
        max_tokens=EVALUATION_LLM_MAX_TOKENS,
    )

    response = evaluator_llm.invoke(prompt)

    content = response.content.strip()

    # Handle markdown JSON if returned
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    scores = json.loads(content)

    return {
        "judge_relevance": float(scores["relevance"]),
        "judge_groundedness": float(scores["groundedness"]),
    }


# ============================================================
# EVALUATION
# ============================================================

def run_evaluation():

    cases = load_cases()

    results = []

    for case in cases:

        print(
            f"\n========== {case['id']} =========="
        )

        try:

            result = run_research_case(case)

            answer = result.get(
                "research_content",
                ""
            )

            contexts = extract_contexts(result)

            ragas_result = run_ragas(
                query=case["query"],
                answer=answer,
                contexts=contexts,
            )

            judge_result = llm_judge(
                query=case["query"],
                answer=answer,
                contexts=contexts,
            )

            result_row = {
                "id": case["id"],
                "query": case["query"],
                "retrieval_success": bool(contexts),
                "synthesis_success": bool(answer),
                **ragas_result,
                **judge_result,
            }

            results.append(result_row)

            print(
                f"Retrieval Success : "
                f"{result_row['retrieval_success']}"
            )

            print(
                f"Synthesis Success : "
                f"{result_row['synthesis_success']}"
            )

            print(
                f"Faithfulness      : "
                f"{result_row.get('faithfulness')}"
            )

            print(
                f"Answer Relevancy  : "
                f"{result_row.get('answer_relevancy')}"
            )

            print(
                f"Judge Relevance   : "
                f"{result_row['judge_relevance']}"
            )

            print(
                f"Judge Groundedness: "
                f"{result_row['judge_groundedness']}"
            )

        except Exception as e:

            print(
                f"ERROR: {repr(e)}"
            )

            results.append(
                {
                    "id": case["id"],
                    "retrieval_success": False,
                    "synthesis_success": False,
                    "error": repr(e),
                }
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    total = len(results)

    retrieval_success = sum(
        r["retrieval_success"]
        for r in results
    )

    synthesis_success = sum(
        r["synthesis_success"]
        for r in results
    )

    faithfulness_scores = [
        r["faithfulness"]
        for r in results
        if r.get("faithfulness") is not None
    ]

    relevancy_scores = [
        r["answer_relevancy"]
        for r in results
        if r.get("answer_relevancy") is not None
    ]

    judge_relevance = [
        r["judge_relevance"]
        for r in results
        if "judge_relevance" in r
    ]

    judge_groundedness = [
        r["judge_groundedness"]
        for r in results
        if "judge_groundedness" in r
    ]

    def average(values):

        if not values:
            return None

        return sum(values) / len(values)

    print("\n==========================================")
    print("RESEARCH OUTPUT QUALITY")
    print("==========================================")

    print(
        f"\nTotal cases       : {total}"
    )

    print(
        f"Retrieval Success : "
        f"{retrieval_success}/{total}"
    )

    print(
        f"Synthesis Success : "
        f"{synthesis_success}/{total}"
    )

    print(
        f"\nRAGAS Faithfulness : "
        f"{average(faithfulness_scores)}"
    )

    print(
        f"RAGAS Relevancy    : "
        f"{average(relevancy_scores)}"
    )

    print(
        f"LLM Judge Relevance: "
        f"{average(judge_relevance)}"
    )

    print(
        f"LLM Judge Grounded : "
        f"{average(judge_groundedness)}"
    )

    print("\n==========================================")

    return results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_evaluation()