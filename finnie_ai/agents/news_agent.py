from utils.state import AgentState
from utils.state_utils import set_state
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from tools.summarize_llm import summarize_article
from utils.stock_mapper import normalize_stock
import time

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def news_agent(state: AgentState) -> AgentState:
    start = time.time()

    state.setdefault("tools_used", []).extend([
        "tavily_search",
        "summarize_article"
    ])

    # -------------------------
    # QUERY
    # -------------------------
    raw_query = state.get("query", "")
    clean_query = raw_query.replace(" news", "").strip()

    query = f"{clean_query} company business news"

    # -------------------------
    # SYMBOL MAPPING
    # -------------------------
    symbol = normalize_stock(clean_query)

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
        # SIMPLE FILTER
        # -------------------------
        if symbol:
            company_keyword = symbol.split(".")[0].lower()
        else:
            company_keyword = clean_query.lower()

        filtered_articles = []

        for article in articles:
            text = (
                (article.get("title") or "") +
                (article.get("content") or "")
            ).lower()

            if company_keyword and company_keyword in text:
                filtered_articles.append(article)

        # ✅ fallback
        articles = filtered_articles if filtered_articles else articles[:3]

        # -------------------------
        # BUILD RESPONSE
        # -------------------------
        response = "📰 Latest News:\n\n"
        processed_articles = []

        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title")
            url = article.get("url", "")
            content = article.get("content") or article.get("snippet") or ""

            summary = summarize_article(content[:2000]) if content else "Summary not available."

            processed_articles.append({
                "title": title,
                "url": url,
                "summary": summary
            })

            response += f"{i}. **{title}**\n\n"
            response += f"{summary}\n\n"
            response += f"[🔗 Read full article]({url})\n\n"

        # -------------------------
        # RETURN STATE
        # -------------------------
        return set_state(
            state,
            start,
            answer=response,
            agent="news_agent",
            confidence=0.9,
            decision_source="news_api",
            answer_source="news_api",
            trace_action="fetch_news",
            extra={
                "news_articles": processed_articles,
                "news_query": clean_query
            }
        )

    except Exception as e:
        return set_state(
            state,
            start,
            answer="❌ Unable to fetch news right now.",
            agent="news_agent",
            confidence=0.4,
            decision_source="news_api",
            answer_source="news_api",
            trace_action="error",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "error_stage": state.get("stage")
            }
        )