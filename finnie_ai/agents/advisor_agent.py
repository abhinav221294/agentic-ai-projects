from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ADVISOR_PROMPT,STOCK_ADVISOR_PROMPT
from tools.rag_pipeline import RAGPipeline
from utils.stock_mapper import normalize_stock
from utils.price_utils import get_price
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
import re
import traceback

rag = RAGPipeline()
DEBUG = False
def is_finance_query(query, llm):
    try:
        res = llm.invoke(f"""
Is this query related to finance, investing, stocks or money?

Query: "{query}"

Answer: yes or no
""").content.lower()
        return "yes" in res
    except:
        return True


def advisor_agent(state: AgentState) -> AgentState:

    profile = state.get("profile") or {}
    memory = state.get("memory", [])

    # -------------------------
    # 🔹 Query
    # -------------------------
    raw_query = (
        memory[-1]["user"].strip()
        if memory and memory[-1].get("user")
        else state.get("query", "").strip()
    )

    query = re.sub(r"[^\w\s]", " ", raw_query).lower().strip()
    llm = get_llm()

    # -------------------------
    # 🔥 DOMAIN FILTER (CRITICAL)
    # -------------------------
    if not is_finance_query(raw_query, llm):
        state["answer"] = "I can only help with finance-related questions."
        state["agent"] = "fallback_agent"
        return state

    # -------------------------
    # 🔹 Symbol
    # -------------------------
    symbol = normalize_stock(raw_query)
    is_stock = symbol is not None

    # -------------------------
    # 🔹 Profile Extraction (FIXED)
    # -------------------------
    if re.search(r"\b([1-9][0-9])\b", query):
        profile["age"] = re.search(r"\b([1-9][0-9])\b", query).group(1)

    if "low risk" in query:
        profile["risk"] = "low"
    elif "medium risk" in query:
        profile["risk"] = "medium"
    elif "high risk" in query:
        profile["risk"] = "high"

    if "income" in query:
        profile["goal"] = "income"
    elif "growth" in query:
        profile["goal"] = "growth"
    elif "safety" in query or "safe" in query:
        profile["goal"] = "safety"

    if "sip" in query:
        profile["investment_type"] = "sip"
    elif "lump sum" in query:
        profile["investment_type"] = "lump sum"

    state["profile"] = profile

    # -------------------------
    # 🔹 Advice detection (FIXED)
    # -------------------------
    STRONG_ADVICE = [
        "should i", "where should i", "how to invest",
        "suggest", "recommend", "portfolio"
    ]

    is_advice = any(p in query for p in STRONG_ADVICE)

    # -------------------------
    # 🔹 Signals
    # -------------------------
    needs_market = is_stock and any(w in query for w in ["price", "current", "latest"])
    needs_news = "news" in query or "update" in query
    needs_risk = "risk" in query or "risky" in query or "safe" in query

    # -------------------------
    # 🔹 Profile completeness
    # -------------------------
    has_risk = profile.get("risk")
    has_goal = profile.get("goal")
    has_type = profile.get("investment_type")

    is_complete = all([has_risk, has_goal, has_type])

    # -------------------------
    # 🔹 Direct recommendation
    # -------------------------
    if is_complete:

        if has_goal == "income" and has_type == "sip":
            allocation = "60% Balanced Advantage Fund\n40% Debt Fund"
        elif has_risk == "low":
            allocation = "30% Equity\n60% Debt\n10% Gold"
        elif has_risk == "high":
            allocation = "80% Equity\n10% Debt\n10% Gold"
        else:
            allocation = "60% Equity\n25% Debt\n15% Gold"

        state["answer"] = f"""
Based on your profile:

Risk: {has_risk}
Goal: {has_goal}
Investment: {has_type.upper()}

Recommended Allocation:
{allocation}
"""
        state["agent"] = "advisor_agent"
        state["confidence"] = "HIGH"
        return state

    # -------------------------
    # 🔹 Ask missing info
    # -------------------------
    if is_advice and not is_complete:
        state["answer"] = """To give the best advice, I need:

1. Risk level (low / medium / high)
2. Goal (growth / income / safety)
3. Investment type (SIP or lump sum)
"""
        state["agent"] = "advisor_agent"
        return state

    # -------------------------
    # 🔹 Market
    # -------------------------
    market_info = ""
    if needs_market:
        try:
            price = get_price(symbol)
            if price:
                market_info = f"{symbol.replace('.NS','')} ≈ ₹{round(price,2)}"
        except:
            pass

    # -------------------------
    # 🔹 News
    # -------------------------
    news_context = ""
    if needs_news:
        try:
            news_context = news_agent({"query": raw_query}).get("answer", "")
        except:
            pass

    # -------------------------
    # 🔹 RAG
    # -------------------------
    is_definition = any(w in query for w in ["what is", "define", "meaning"])
    context_docs = ""

    if is_definition:
        results = rag.retrieve(query=query)
        if results:
            context_docs = results[0].get("content", "")

    # -------------------------
    # 🔹 Final LLM (ONE CALL)
    # -------------------------
    prompt = f"""
User Query: {raw_query}

Context:
{context_docs}

Market: {market_info}
News: {news_context}

Give a concise financial response.
"""

    try:
        answer = llm.invoke(prompt).content
    except:
        answer = "Unable to process request."

    state.update({
        "answer": answer,
        "agent": "advisor_agent",
        "confidence": "MEDIUM"
    })

    return state