from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ADVISOR_PROMPT
from tools.rag_pipeline import RAGPipeline
from utils.stock_mapper import normalize_stock
from utils.price_utils import get_price
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent

import json
import re

rag = RAGPipeline()


def advisor_agent(state: AgentState) -> AgentState:

    # -------------------------
    # 🔹 Query cleaning
    # -------------------------
    raw_query = state["query"].replace("'", "").replace('"', "").strip()
    query = re.sub(r"[^\w\s]", " ", raw_query.lower()).strip()

    memory = state.get("memory", [])


    # -------------------------
    # 🔹 Last answer
    # -------------------------
    last_answer = next(
        (m["assistant"] for m in reversed(memory) if m.get("assistant")),
        ""
    )

    # -------------------------
    # 🔹 Combined query
    # -------------------------
    user_inputs = [m.get("user", "") for m in memory if m.get("user")]
    user_inputs = [u for u in user_inputs if u.lower().strip() != raw_query.lower().strip()]

    combined_query = " ".join(user_inputs + [raw_query])
    combined_query = re.sub(r"[^\w\s]", " ", combined_query).strip().lower()
    
    symbol = normalize_stock(raw_query)

    # ✅ Only allow symbol if explicitly stock-related
    is_stock_query = any(w in query for w in ["stock", "share", "price"])

    if not is_stock_query:
        symbol = None

    price_keywords = ["price", "quote", "current", "latest"]
    needs_risk = any(w in combined_query for w in ["risk", "safe", "danger", "volatile", "stable"])    
    needs_market = symbol is not None and any(w in combined_query for w in price_keywords)
    needs_news = any(w in combined_query for w in ["news", "latest"])

    is_advice_query = any(w in combined_query for w in [
        "should i invest",
        "where should i invest",
        "investment plan",
        "portfolio",
        "suggest",
        "allocate"
        ])
    
    is_risk_question = any(w in combined_query for w in ["risk", "risky"]) and "?" in raw_query

    if symbol and is_risk_question:
        # Let LLM handle using risk + market context
        is_advice_query = False

    if not (needs_risk or needs_market or needs_news):
            print("👉 Advisor handling directly (no agents)")
    
    risk_analysis = ""
    market_info = ""
    news_context = ""

    if needs_risk:
        
        try:
            risk_state = {
            "query": combined_query,
            "memory": memory
            }
            risk_result = risk_agent(risk_state)
            risk_analysis = risk_result.get("answer", "")
        except Exception as e:
            print("⚠️ Risk agent failed:", e)
            risk_analysis = ""


    if needs_market:
        try:
        
            price = None
            
            if symbol:
                if symbol:
                    price = get_price(symbol)
                else:
                    price = None
            else:
                print("⚠️ Could not detect stock symbol")
            if price:
                clean_price = round(price, 2)
                stock_name = symbol.replace(".NS", "")
                market_info = f"{stock_name} is currently trading around ₹{clean_price}"

        except Exception as e:
                print("⚠️ Market fetch failed:", e)
                market_info = ""

    if needs_news or (needs_market and len(combined_query.split()) > 3):  # market queries also benefit from news
        try:
            news_state = {
            "query": combined_query
            }
            news_result = news_agent(news_state)
            news_context = news_result.get("answer", "")
            news_context = news_context[:1000] if news_context else ""
        except Exception as e:
            print("⚠️ News agent failed:", e)
            news_context = ""


    # -------------------------
    # 🔹 RAG retrieval (rule-based)
    # -------------------------
    is_definition = any(q in combined_query for q in [
        "what is", "define", "explain", "how", "difference", "meaning"
    ])

    is_advice = any(q in combined_query for q in [
        "invest", "should i", "buy", "portfolio"
    ])

    rag_results = rag.retrieve(query=combined_query) if is_definition and not is_advice else []

    context_docs = "\n\n".join(r.get("content", "") for r in rag_results[:2])
    knowledge_section = context_docs if context_docs.strip() else "None"

    # -------------------------
    # 🔹 Profile detection
    # -------------------------
    has_risk = any(w in combined_query for w in ["low", "medium", "high", "safe", "risk"])
    has_goal = any(w in combined_query for w in ["growth", "income", "safety", "returns"])
    has_type = any(w in combined_query for w in ["sip", "lump", "lumpsum", "one"])

    is_profile_complete = has_risk and has_goal and has_type
    if is_advice_query:
        clarification_needed = not is_profile_complete
    else:
        clarification_needed = False


    if is_advice_query and not is_profile_complete:

        missing = []

        if not has_risk:
            missing.append("Risk level (low / medium / high)")
        if not has_goal:
            missing.append("Goal (growth / income / safety)")
        if not has_type:
            missing.append("Investment type (SIP or lump sum)")

        # ✅ If user already gave risk → still give starter recommendation
        if has_risk:
            allocation = "70% Balanced Advantage Fund + 30% Short-term Debt Fund"

            state["answer"] = f"""Based on your preference for low risk:

Recommendation  
{allocation}

This gives stability with limited volatility.

To refine further, I need:
""" + "\n".join(f"{i+1}. {m}" for i, m in enumerate(missing))

        else:
            state["answer"] = "To give you the best investment recommendation, I need:\n" + \
                         "\n".join(f"{i+1}. {m}" for i, m in enumerate(missing))

        state["agent"] = "advisor_agent"
        state["confidence"] = "MEDIUM"
        state["clarification_needed"] = True

        return state
    
    # -------------------------
    # 🔹 Mode detection
    # -------------------------
    if any(s in combined_query for s in ["detail", "explain more", "clarify"]):
        mode = "DETAIL"
    else:
        mode = "AUTO"

    # -------------------------
    # 🔹 Strategy (only if needed)
    # -------------------------
    allocation = ""
    risk = strategy = goal = horizon = ""

    llm = get_llm()

    if mode != "DETAIL" and is_profile_complete:
        try:
            strategy_prompt = f"""
Extract structured investment strategy.

Return JSON:
{{
  "risk": "...",
  "strategy": "...",
  "user_goal": "...",
  "time_horizon": "...",
  "allocation": "..."
}}

Query:
{combined_query}
"""
            content = llm.invoke(strategy_prompt).content.strip()

            # Extract JSON safely
            match = re.search(r"\{.*\}", content, re.DOTALL)

            if match:
                try:
                    parsed = json.loads(match.group())
                except:
                    parsed = {}
            else:
                    parsed = {}

            risk = parsed.get("risk", "")
            strategy = parsed.get("strategy", "")
            goal = parsed.get("user_goal", "")
            horizon = parsed.get("time_horizon", "")
            allocation = parsed.get("allocation", "")
            if not allocation:
                if "low" in combined_query:
                    allocation = "70% Balanced Advantage Fund + 30% Short-term Debt Fund"

        except Exception as e:
            print("⚠️ Strategy parse failed:", e)

    # -------------------------
    # 🔹 Fallback allocation
    # -------------------------
    if is_profile_complete and not allocation.strip():
        if "low" in combined_query:
            allocation = "70% Balanced Advantage Fund + 30% Short-term Debt Fund"
        elif "high" in combined_query:
            allocation = "80% Nifty 50 Index Fund + 20% Balanced Advantage Fund"
        else:
            allocation = "60% Nifty 50 Index Fund + 40% Balanced Advantage Fund"

    if not is_profile_complete:
        allocation = ""

    # -------------------------
    # 🔹 Conversation
    # -------------------------
    conversation = "\n".join(
        f"User: {m.get('user','')}\nAssistant: {m.get('assistant','')}"
        for m in memory[-3:]
    ) or "None"

    # -------------------------
    # 🔹 Final Prompt
    # -------------------------
    final_prompt = f"""{ADVISOR_PROMPT}

### RESPONSE MODE
{mode}

### USER QUERY
{combined_query}

### CLARIFICATION NEEDED
{clarification_needed}

### PREVIOUS RECOMMENDATION
{last_answer or "None"}

### CONTEXT
{conversation}

### RISK ANALYSIS
{risk_analysis or "None"}

### MARKET INFO
{market_info or "None"}

### PORTFOLIO ALLOCATION
{allocation or "None"}

### NEWS CONTEXT
{news_context or "None"}

### KNOWLEDGE
{knowledge_section}

CONTEXT USAGE RULE:

If RISK ANALYSIS is provided:
- You MUST consider it before answering

If MARKET INFO is provided:
- Use it to ground your advice

If NEWS CONTEXT is provided:
- Consider recent sentiment before recommending
"""



    # -------------------------
    # 🔹 LLM Response
    # -------------------------
    answer = ""
    try:
        response = llm.invoke(final_prompt)
        answer = getattr(response, "content", "") or ""

        confidence = "LOW"

        if risk_analysis or market_info or news_context:
                confidence = "MEDIUM"

        if context_docs and (market_info or news_context):
                confidence = "HIGH"

    except Exception as e:
        print("❌ FINAL ERROR:", e)

        if not is_profile_complete:
            answer = """To give you the best investment recommendation, I need:

1. Risk level (low / medium / high)
2. Goal (growth / income / safety)
3. Investment type (SIP or lump sum)"""
        else:
            answer = f"""Recommendation
{allocation}

Breakdown
Balanced allocation based on your profile.

Why this works
Balances risk and income.

Next Steps
Invest and review periodically."""

        confidence = "LOW"

    # -------------------------
    # 🔹 Final state
    # -------------------------



    state.update({
        "answer": answer,
        "agent": "advisor_agent",
        "confidence": confidence,
        "clarification_needed": clarification_needed
    })

    return state