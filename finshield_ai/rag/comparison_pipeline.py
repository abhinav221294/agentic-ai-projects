from rag.loader import load_pdf
from prompts.prompt import COMPARE_PROMPT
from llm.groq_client import llm
from dotenv import load_dotenv
import os

load_dotenv()


def compare_policies(pdf_path_a, pdf_path_b):

    text_a = load_pdf(pdf_path_a)
    text_b = load_pdf(pdf_path_b)

    prompt = COMPARE_PROMPT.format(
        policy_a=text_a[:8000],
        policy_b=text_b[:8000]
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": []
    }