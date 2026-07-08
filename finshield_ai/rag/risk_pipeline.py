from rag.vector_store import retrieve
from prompts.prompt import RISK_PROMPT
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_risk():

    response = retrieve(
        "Identify the major risks and exclusions in this insurance policy."
    )

    docs = response["documents"][0]

    context = "\n\n".join(docs)

    prompt = RISK_PROMPT.format(
        context=context
    )

    answer = llm.invoke(prompt)

    return {
        "answer": answer.content,
        "sources": docs
    }