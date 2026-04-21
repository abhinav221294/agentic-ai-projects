from langchain_openai import ChatOpenAI

def get_llm(temperature=0.3):
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature
    )