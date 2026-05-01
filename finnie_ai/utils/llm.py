from langchain_openai import ChatOpenAI

def get_llm(model="gpt-4o-mini", temperature=0.2, max_tokens=500):
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )