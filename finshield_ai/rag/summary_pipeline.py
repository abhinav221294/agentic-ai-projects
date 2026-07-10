from rag.loader import load_pdf
from prompts.prompt import SUMMARY_PROMPT
from llm.groq_client import get_llm
from app.utils.token_usage import get_token_usage

llm = get_llm()

def generate_summary(pdf_path):

    text = load_pdf(pdf_path)

    # Limit context if document is large
    context = text[:12000]

    prompt = SUMMARY_PROMPT.format(
        context=context
    )

    response = llm.invoke(prompt)
    usage = get_token_usage(response)

    return {
        "answer": response.content,
        "sources": [],
        "usage": usage
    }