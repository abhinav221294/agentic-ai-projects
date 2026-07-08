from rag.vector_store import retrieve
from prompts.prompt import SUMMARY_PROMPT
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_summary():

    response = retrieve(
        "Provide an overview of the insurance policy."
    )

    docs = response["documents"][0]

    context = "\n\n".join(docs)

    prompt = SUMMARY_PROMPT.format(
        context=context
    )

    answer = llm.invoke(prompt)

    return {
        "answer": answer.content,
        "sources": docs
    }