from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.config import GROQ_MODEL
import os

load_dotenv()

llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=os.getenv("GROQ_API_KEY")
)