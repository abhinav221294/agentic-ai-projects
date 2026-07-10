from datasets import Dataset
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from evaluation.metrics import METRICS
from llm.groq_client import get_llm

import os

load_dotenv()


# ----------------------------
# Judge LLM (Groq)
# ----------------------------

judge_llm = LangchainLLMWrapper(
    ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )
)


# ----------------------------
# Embedding Model
# ----------------------------

embedding_model = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
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