from utils.state import AgentState
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from tools.summarize_text import summarize_article


load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def news_agent(state:AgentState)-> AgentState:
    
    query = f"{state['query']} latest news"

    try:
        results = client.search(
            query=query,
            topic="news",
            max_results=5
        )
        articles = results.get("results",[])

        if not articles:
            raise Exception("No news found")
        response = "📰 Latest News:\n\n"

        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            url = article.get("url", "")
            content = article.get("content", "") or article.get("snippet", "")
            summary = summarize_article(content[:2000])

            response += f"{i}. {title}\n\n"
            response += f"{summary}\n\n"
            response += f"For detail:\n{url}\n\n"

        
        state["answer"] = response
        state["agent"] = "news_agent"
        state["confidence"] = "HIGH"


    except Exception as e:
        state["answer"] = "❌ Unable to fetch news right now."
        state["agent"] = "news_agent"
        state["confidence"] = "LOW"
    
    return state