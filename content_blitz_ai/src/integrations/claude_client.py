from langchain_anthropic import ChatAnthropic


def claude_client_llm(
    model="claude-haiku-4-5-20251001",
    #"claude-sonnet-4-20250514",
    temperature=0.1,
    max_tokens=512,
    streaming=False,
    timeout=60,
    max_retries=3
):

    return ChatAnthropic(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
        timeout=timeout,
        max_retries=max_retries
    )