from rag.vector_store import retrieve
#from transformers import pipeline
from prompts.prompt import INSURANCE_PROMPT
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os


load_dotenv()

#generator = pipeline(
#    "text-generation",
#    model="microsoft/Phi-3-mini-4k-instruct"
#)

llm = ChatGroq(

    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
    )

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