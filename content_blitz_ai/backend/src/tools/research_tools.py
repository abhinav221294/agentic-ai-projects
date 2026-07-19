from langchain.tools import tool
from src.integrations.perplexity_client import perplexity_search


@tool
def web_search_tool(query: str):

    """
    Performs web research using Perplexity AI.
    """

    return perplexity_search(query)