from rag.loader import load_pdf
from prompts.prompt import RISK_PROMPT
from llm.groq_client import get_llm
from app.utils.token_usage import get_token_usage

llm = get_llm()

def analyze_risk(pdf_path):

    text = load_pdf(pdf_path)

    # Limit context for large PDFs
    context = text[:12000]

    prompt = RISK_PROMPT.format(
        context=context
    )

    response = llm.invoke(prompt)
    usage = get_token_usage(response)

    return {
        "answer": response.content,
        "sources": [],
        "usage": usage
    }