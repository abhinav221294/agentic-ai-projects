from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ADVISOR_PROMPT
from agents.market_agent import get_finnhub_price
from tools.rag_pipeline import RAGPipeline
import json
from utils.stock_mapper import STOCK_MAP,normalize_stock
from utils.price_utils import get_price

rag = RAGPipeline()

def advisor_agent(state: AgentState) -> AgentState:

    raw_query = state["query"]
    query = raw_query.lower()

    memory = state.get("memory", [])
    #context_text = " ".join([m.get("user", "") for m in memory[-3:]]).lower()
    full_query = query

    # -------------------------
    # Market info
    # -------------------------

    market_info = ""

    if any(word in query for word in ["stock", "price", "buy", "sell"]):
            symbol = normalize_stock(raw_query)
            price = get_price(symbol)

            if price:
                market_info = f"{symbol} current price is {price}"

    retrieval_prompt = f"""
Decide whether this query needs knowledge retrieval.

Return ONLY:
YES or NO

Rules:
- YES → if query is asking for definition, concept, explanation
- NO → if query is asking for advice, recommendation, decision

Query:
{full_query}
"""
    llm = get_llm()
    retrieval_decision = llm.invoke(retrieval_prompt).content.strip().upper()

    if "YES" in retrieval_decision:
        rag_results = rag.retrieve(query=query) or []
    else:
        rag_results = []

    context_docs = "\n\n".join(
        r.get("content", "") for r in rag_results[:2]
    )

    if context_docs.strip() and retrieval_decision == "YES":
        knowledge_section = context_docs
    else:
        knowledge_section = "None"

    # -------------------------
    # Conversation
    # -------------------------
    conversation = ""
    for m in memory[-3:]:
        conversation += f"\nUser: {m.get('user', '')}\nAssistant: {m.get('assistant', '')}\n"

    detail_signals = [
    "in detail",
    "more details",
    "explain more",
    "not clear",
    "don't understand",
    "clarify"
    ]

    # -------------------------
    # 🔥 STEP 1: Strategy (JSON)
    # -------------------------
    strategy_prompt = f"""You are an expert financial analyst.

Your job is NOT just to classify.

You MUST:
- deeply understand the user context
- generate a personalized investment approach

Extract:
- risk tolerance
- strategy
- user goal
- time horizon
- recommended portfolio allocation (in %)
- reasoning

Return STRICT JSON:
{{
  "risk": "...",
  "strategy": "...",
  "user_goal": "...",
  "time_horizon": "...",
  "allocation": "e.g. 60% balanced fund + 40% index fund",
  "reason": "..."
}}

IMPORTANT:
- The allocation MUST be different for different users
- Do NOT give generic outputs

Query:
{full_query}
"""

    try:

        simple_signals = [
    "where should i invest",
    "should i invest",
    "what should i do"
        ]


        detail_signals = [
        "in detail",
        "more details",
        "explain more",
        "not clear",
        "don't understand",
        "clarify"
        ]

        if any(s in query for s in detail_signals):
            mode = "DETAIL"
        elif any(s in query for s in simple_signals):
            mode = "SIMPLE"
        else:
            mode = "AUTO"

      
        if mode != "DETAIL":
            strategy_response = llm.invoke(strategy_prompt)

            parsed = json.loads(
                strategy_response.content.strip().replace("```json", "").replace("```", "")
            )

            strategy = parsed.get("strategy", "unknown")
            risk = parsed.get("risk", "unknown")
            #reason = parsed.get("reason", "")
            goal = parsed.get("user_goal", "")
            horizon = parsed.get("time_horizon", "")
            allocation = parsed.get("allocation", "")
        else:
            # 🔥 DO NOT recompute for follow-ups
            strategy = "same as previous"
            risk = "same as previous"
            goal = ""
            horizon = ""
            allocation = ""
        
        if mode != "DETAIL":
            if not allocation or allocation.strip() == "":
                allocation = "60% Nifty 50 index fund + 40% balanced advantage fund"

    except Exception:
        strategy = "balanced"
        risk = "medium"
        #reason = ""
    
    profile_section = f"""- Risk: {risk}
- Strategy: {strategy}"""

    if goal:
        profile_section += f"\n- Goal: {goal}"
    if horizon:
        profile_section += f"\n- Time Horizon: {horizon}"

    last_answer = ""

    for m in reversed(memory):
        if m.get("assistant"):
            last_answer = m["assistant"]
            break
    allocation_section = allocation if mode != "DETAIL" else "Use previous recommendation"
    # -------------------------
    # 🔥 STEP 2: Generate answer
    # -------------------------
    final_prompt = f"""{ADVISOR_PROMPT}

### RESPONSE MODE
{mode}

### USER QUERY
{full_query}

### PREVIOUS RECOMMENDATION
{last_answer if last_answer else "None"}

### CONTEXT (Recent Conversation)
{conversation if conversation else "None"}

- Risk: {risk}
- Strategy: {strategy}
- Goal: {goal}
- Time Horizon: {horizon}

### USER PROFILE (Inferred)
{profile_section}

### PORTFOLIO / MARKET CONTEXT
{market_info if market_info else "None"}

### PORTFOLIO ALLOCATION (MANDATORY - MUST FOLLOW)
{allocation_section}

### RELEVANT KNOWLEDGE
{knowledge_section}

If RESPONSE MODE != DETAIL and allocation is provided:
- You MUST use it

If RESPONSE MODE = DETAIL:
- Ignore PORTFOLIO ALLOCATION
- Use PREVIOUS RECOMMENDATION instead

DETAIL MODE (CRITICAL):

If RESPONSE MODE = DETAIL:
- You MUST use the structure below
- You MUST expand the answer
- You MUST NOT give a short answer


Required Structure:

Recommendation
-Provide allocation in %.

If user has provided budget:
- also include ₹ split
Else:
- DO NOT include ₹ values

Breakdown
- Explain each investment and its role

Why this works
- Explain how allocation balances risk and return

Next Steps
- Clear actionable steps (platform + SIP split)

If this structure is not followed, the answer is INVALID.

- Avoid repeating the same sentence
- Add clarity, not length
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