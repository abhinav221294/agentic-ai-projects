from datasets import Dataset
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from evaluation.metrics import METRICS
from llm.groq_client import get_llm
from app.config import EMBEDDING_MODEL_NAME

EMBEDDING_MODEL_NAME_FULL = "sentence-transformers/" + EMBEDDING_MODEL_NAME

# ----------------------------
# Judge LLM (Groq)
# ----------------------------

judge_llm = LangchainLLMWrapper(
    get_llm()
)


# ----------------------------
# Embedding Model
# ----------------------------

embedding_model = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME_FULL
    )
)


# ----------------------------
# Evaluation
# ----------------------------

def evaluate_response(
    question,
    answer,
    contexts,
    ground_truth
):

    dataset = Dataset.from_dict(
        {
            "question": [question],
            "answer": [answer],
            "contexts": [contexts],
            "ground_truth": [ground_truth]
        }
    )

    result = evaluate(
        dataset=dataset,
        metrics=METRICS,
        llm=judge_llm,
        embeddings=embedding_model
    )

    return result.to_pandas()