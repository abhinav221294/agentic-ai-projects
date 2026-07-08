from rag.loader import load_pdf
from prompts.prompt import RISK_PROMPT
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)


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