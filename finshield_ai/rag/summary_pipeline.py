from rag.loader import load_pdf
from prompts.prompt import SUMMARY_PROMPT
from app.llm.groq_client import llm

def generate_summary(pdf_path):

    text = load_pdf(pdf_path)

    # Limit context if document is large
    context = text[:12000]

    prompt = SUMMARY_PROMPT.format(
        context=context
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "sources": []      # Keep response format consistent
    }