from langchain_google_genai import ChatGoogleGenerativeAI


def gemini_llm_client(
    model="gemini-2.5-flash",
    temperature=0.1,
    max_tokens=512,
    timeout=60,
    max_retries=2
):

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries
    )