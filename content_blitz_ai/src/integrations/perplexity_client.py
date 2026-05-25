import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def __perplexity_client_llm():

    client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
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

    return response.choices[0].message.content