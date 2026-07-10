from rag.vector_store import retrieve
#from transformers import pipeline
from prompts.prompt import INSURANCE_PROMPT
from llm.groq_client import get_llm
from app.utils.token_usage import get_token_usage

llm = get_llm()

def ask_question(question):

    response = retrieve(question)

    docs = response["documents"][0]

    context = "\n\n".join(docs)

    prompt = INSURANCE_PROMPT.format(context=context, question=question)

    result = llm.invoke(prompt)
    usage = get_token_usage(response)

    return {

    "answer": result.content,

    "sources": docs,
    "usage": usage

}