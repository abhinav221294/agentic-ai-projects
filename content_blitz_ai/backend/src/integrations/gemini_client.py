from langchain_google_genai import ChatGoogleGenerativeAI


def gemini_llm_client(
    model="gemini-3.5-flash-lite",
    temperature=0.1,
    max_tokens=512,
    timeout=60,
    max_retries=2
):

    #print("\n========== GEMINI CONFIG ==========")
    #print("model:", model)
    #print("temperature:", temperature)
    #print("max_tokens:", max_tokens)
    #print("timeout:", timeout)
    #print("===================================\n")

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries
    )