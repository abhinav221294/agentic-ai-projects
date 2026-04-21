from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ADVISOR_PROMPT
from agents.market_agent import get_finnhub_price
from tools.rag_pipeline import RAGPipeline
import json

rag = RAGPipeline()

def advisor_agent(state: AgentState) -> AgentState:

    raw_query = state["query"]
    query = raw_query.lower()

    memory = state.get("memory", [])
    context_text = " ".join([m.get("user", "") for m in memory[-3:]]).lower()
    full_query = context_text + " " + query

    # -------------------------
    # Market info
    # -------------------------
    stock_map = {
        "tesla": "TSLA",
        "apple": "AAPL",
        "reliance": "RELIANCE.NS"
    }

    market_info = ""

    for name, symbol in stock_map.items():
        if name in query:
            price = get_finnhub_price(symbol)
            if price:
                market_info = f"{name.capitalize()} ({symbol}) current price is {price}"
            break

    rag_results = rag.retrieve(query=query) or []

    context_docs = "\n\n".join(
        r.get("content", "") for r in rag_results[:2]
    )

    context_docs = context_docs if context_docs.strip() else "No relevant knowledge found."

    # -------------------------
    # Conversation
    # -------------------------
    conversation = ""
    for m in memory[-3:]:
        conversation += f"\nUser: {m.get('user', '')}\nAssistant: {m.get('assistant', '')}\n"

    llm = get_llm()

    # -------------------------
    # 🔥 STEP 1: Strategy (JSON)
    # -------------------------
    strategy_prompt = f"""
You are an expert financial analyst.

Deeply analyze the user's intent, not just classify.

Extract:
- risk tolerance (low / medium / high)
- investment strategy (conservative / balanced / aggressive)
- user goal (wealth, income, safety, etc.)
- time horizon (short / medium / long)
- reasoning (why)

Return STRICT JSON only:
{{
  "risk": "low/medium/high/unknown",
  "strategy": "conservative/balanced/aggressive/unknown",
  "user_goal": "...",
  "time_horizon": "...",
  "reason": "..."
}}

Be precise and infer missing details if needed.

Query:
{full_query}
"""

    try:
        strategy_response = llm.invoke(strategy_prompt)

        parsed = json.loads(
            strategy_response.content.strip().replace("```json", "").replace("```", "")
        )

        strategy = parsed.get("strategy", "unknown")
        risk = parsed.get("risk", "unknown")
        reason = parsed.get("reason", "")
        goal = parsed.get("user_goal", "")
        horizon = parsed.get("time_horizon", "")

    except Exception:
        strategy = "balanced"
        risk = "medium"
        reason = ""

    # -------------------------
    # 🔥 STEP 2: Generate answer
    # -------------------------
    final_prompt = f"""{ADVISOR_PROMPT}

You are a thoughtful financial advisor.

Your job is to:
1. Understand the user's situation
2. Analyze risk tolerance and goals
3. Compare options if needed
4. Provide clear, structured advice

Conversation:
{conversation}

User Query:
{full_query}

Inferred Risk Profile (may be uncertain): {risk}
Inferred Strategy (may be uncertain): {strategy}
Inference Reason: {reason}

Relevant Knowledge:
{context_docs}

Market Data:
{market_info}

User Goal:
{goal}

Time Horizon: 
{horizon}

IMPORTANT:
- First internally analyze the problem step-by-step.
-Then produce the final structured answer.
-Do NOT skip reasoning.
- If query is complex, break it into parts
- If comparing options, show pros & cons
- Always justify your recommendation
- Use the "Relevant Knowledge" section if it is useful. Do not ignore it.
- If user intent is unclear, make reasonable assumptions and proceed.

OUTPUT FORMAT:

Decision
- (Clear stance: Yes / No / Conditional)

Understanding of User
Analysis
Recommendation
Suggested Options:
- ALWAYS write options like:
  1. Equity Mutual Funds
     - Pros: ...
     - Cons: ...
  2. Fixed Deposits
     - Pros: ...
     - Cons: ...

- NEVER break number and title into separate lines
- DO NOT write:
  1.
  Equity Mutual Funds

Keep it simple but insightful.
IMPORTANT:
- Do NOT assume user risk profile unless explicitly stated
- If information is missing, clearly say assumptions
- Use phrases like:
  - "If your risk tolerance is..."
  - "Assuming a moderate risk level..."
- Avoid stating user preferences as facts

CRITICAL INSTRUCTION:
- The inferred risk profile and strategy may be uncertain
- Do NOT assume them as facts
- If user has not explicitly stated preferences, acknowledge uncertainty
- Use conditional language like:
  - "If your risk tolerance is..."
  - "Assuming a moderate risk profile..."
- Never state inferred traits as confirmed facts
- You MUST take a stance when possible:
  - "Yes, but..."
  - "No, unless..."
  - "Only if..."
- Do not stay neutral unless necessary
- Avoid generic advice like "diversify" unless it adds value
"""

    try:
        response = llm.invoke(final_prompt)
        answer = response.content
        
        if context_docs != "No relevant knowledge found." and market_info:
            confidence = "HIGH"
        elif context_docs != "No relevant knowledge found.":
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

    except Exception:
        answer = f"A {strategy} strategy is recommended based on your query."
        confidence = "LOW"

    # -------------------------
    # Final state
    # -------------------------
    state["answer"] = answer
    state["agent"] = "advisor_agent"
    state["confidence"] = confidence
    state["clarification_needed"] = False

    return state