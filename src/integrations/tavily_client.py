# src/integrations/tavily_client.py

import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def __tavily_client():

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment variables")

    client = TavilyClient(api_key=api_key)

    return client


def tavily_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "advanced"
):

    client = __tavily_client()

    response = client.search(
        query=query,
        search_depth=search_depth,
        max_results=max_results
    )

    return response