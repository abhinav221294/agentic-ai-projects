from src.core.config import PERPLEXITY_API_KEY
from openai import OpenAI

def __perplexity_client_llm():

    client = OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )

    return client


def perplexity_search(
    query: str,
    model: str = "sonar",
    temperature: float = 0.1
):

    client = __perplexity_client_llm()

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": query
            }
        ]
    )

    content = response.choices[0].message.content
    citations = response.citations or []

    return {
        "results": [
            {
                "title": "Perplexity Research",
                "content": content,
                "citations": citations
            }
        ]
    }

