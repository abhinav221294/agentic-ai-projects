from rag.vector_store import retrieve
#from transformers import pipeline
from prompts.prompt import INSURANCE_PROMPT
from app.llm.groq_client import llm


def ask_question(question):

    response = retrieve(question)

    docs = response["documents"][0]

    context = "\n\n".join(docs)

    prompt = INSURANCE_PROMPT.format(context=context, question=question)

    result = llm.invoke(prompt)

    return {

    "answer": result.content,

    "sources": docs

}