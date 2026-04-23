from utils.llm import get_llm

def summarize_article(content: str) -> str:
    if not content:
        return "Summary not available."

    llm = get_llm(temperature=0.3)

    prompt = f"""
    Summarize the following news article in 120-180 words.

    Focus on:
    - Key event
    - Business/financial impact
    - Important facts

    Article:
    {content}
    """

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except:
        return "Summary generation failed."