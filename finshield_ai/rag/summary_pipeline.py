from rag.loader import load_pdf
from prompts.prompt import SUMMARY_PROMPT
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)


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