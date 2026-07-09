from rag.loader import load_pdf
from prompts.prompt import RISK_PROMPT
from app.llm.groq_client import llm


def analyze_risk(pdf_path):

    text = load_pdf(pdf_path)

    # Limit context for large PDFs
    context = text[:12000]

    prompt = RISK_PROMPT.format(
        context=context
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": []
    }