from langchain_openai import ChatOpenAI

def get_llm(temperature=0.2, max_tokens=500):
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        max_tokens=max_tokens
    )