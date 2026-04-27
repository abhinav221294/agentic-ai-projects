from utils.state import AgentState
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from tools.summarize_text import summarize_article
from utils.stock_mapper import normalize_stock
import time

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
def _set(state, start, answer, confidence, answer_source, extra=None):
    state["answer"] = answer
    state["agent"] = "news_agent"
    state["confidence"] = confidence
    state["decision_source"] = "tool"
    state["answer_source"] = answer_source
    state["execution_time"] = round(time.time() - start, 2)

    if extra:
        state.update(extra)

    return state


def news_agent(state: AgentState) -> AgentState:
    start = time.time()

    state.setdefault("tools_used", []).extend([
        "tavily_search",
        "summarize_article"
    ])

    query = f"{state['query']} latest news"
    symbol = normalize_stock(state["query"])

    try:
        results = client.search(
            query=query,
            topic="news",
            max_results=5
        )

        articles = results.get("results", [])

        if not articles:
            raise Exception("No news found")

        # -------------------------
        # FILTER BY COMPANY
        # -------------------------
        company_keyword = None
        if symbol:
            company_keyword = symbol.split(".")[0].lower()

        filtered_articles = []
        for article in articles:
            text = ((article.get("title") or "") + (article.get("content") or "")).lower()
            if company_keyword and company_keyword in text:
                filtered_articles.append(article)

        articles = filtered_articles if filtered_articles else articles[:3]

        # -------------------------
        # BUILD RESPONSE
        # -------------------------
        response = "📰 Latest News:\n\n"

        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            url = article.get("url", "")
            content = article.get("content", "") or article.get("snippet", "")

            summary = summarize_article(content[:2000]) if content else "Summary not available."

            response += f"{i}. {title}\n\n"
            response += f"{summary}\n\n"
            response += f"For detail:\n{url}\n\n"

        return _set(
            state, start,
            response,
            0.9,
            "news_api"
        )

    except Exception as e:
        return _set(
            state, start,
            "❌ Unable to fetch news right now.",
            0.4,
            "news_api",
            {"error": str(e)}
        )