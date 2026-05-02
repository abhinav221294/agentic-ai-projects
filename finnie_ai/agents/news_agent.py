from utils.state import AgentState
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from tools.summarize_text import summarize_article
from utils.stock_mapper import normalize_stock
import time
import re
from utils.llm import get_llm



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

def is_followup(query, memory):
    history = "\n".join([
        f"User: {m.get('query')}\nAssistant: {m.get('assistant')}"
        for m in memory[-2:]
    ])

    prompt = f"""Is the user asking a follow-up question based on previous response?

Conversation:
{history}

New query:
{query}

Answer only YES or NO.
"""
    try:
        res = llm.invoke(prompt)
        return "yes" in res.content.lower()
    except:
        return False



def news_agent(state: AgentState) -> AgentState:

    state.setdefault("trace", []).append({
    "agent": "news_agent",
    "action": "fetch_news"
    })  

    start = time.time()

    tools = state.setdefault("tools_used", [])

    if "tavily_search" not in tools:
        tools.append("tavily_search")

    if "summarize_article" not in tools:
        tools.append("summarize_article")

    query = f"{state.get('query', '')} latest news"
    query = re.sub(r'[^a-z\s]', '',query).lower().strip()
    symbol = normalize_stock(state.get("query", ""))
    articles = state.get("news_articles", [])

    memory = state.get("memory", [])

    if state.get("news_articles") and is_followup(state.get("query", ""), memory):

        articles = state.get("news_articles", [])

        summary_text = "📰 Summary of latest news:\n\n"

        for i, article in enumerate(articles[:3], 1):
            summary_text += f"{i}. {article['title']}\n"
            summary_text += f"- {article.get('summary', '')[:200]}\n\n"

        return _set(
        state, start,
        summary_text,
        0.9,
        "memory"
        )   
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

        if company_keyword:
            filtered_articles = []
            for article in articles:
                text = ((article.get("title") or "") + (article.get("content") or "")).lower()
                if company_keyword in text:
                    filtered_articles.append(article)

            articles = filtered_articles if filtered_articles else articles[:3]
        
        # -------------------------
        # PROCESS ARTICLES
        # -------------------------

        processed_articles = []

        for article in articles:
            content = article.get("content") or article.get("snippet") or ""
            summary = summarize_article(content[:2000]) if content else "Summary not available."

            processed_articles.append({
                "title": article.get("title"),
                "url": article.get("url"),
                "summary": summary
                })
        # -------------------------
        # BUILD RESPONSE
        # -------------------------
        response = "📰 Latest News:\n\n"
            
        for i, article in enumerate(processed_articles, 1):
                response += f"{i}. {article['title']}\n\n"
                response += f"{article['summary']}\n\n"
                response += f"For detail:\n{article['url']}\n\n"

        extra = {
            "news_articles": processed_articles,
            "news_query": query,
            "news_symbol": symbol
            }


        return _set(
            state, start,
            response,
            0.9,
            "news_api",
            extra=extra
        )

    except Exception as e:
        return _set(
            state, start,
            "❌ Unable to fetch news right now.",
            0.4,
            "news_api",
            {"error": str(e)}
        )