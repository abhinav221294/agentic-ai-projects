from utils.state import AgentState
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent
import re
import time
import json
import random
import hashlib
from utils.llm import get_llm
from utils.finance_constants import (ALLOCATION_MAP,MAX_LIMITS,
FUND_SUGGESTIONS)
from utils.fund_utils import extract_user_allocation,merge_allocation
from utils.format_utils import alloc
from utils.calculation_utils import calculate_lumpsum_future_value,calculate_sip_future_value
from utils.state_utils import set_state
from utils.parsing_utils import normalize_term
from dotenv import load_dotenv
load_dotenv()
# Load environment variables (API keys etc.)

# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
#def set_state(state, start, answer, agent, confidence, decision_source, answer_source, trace_type, extra=None):
#    state["answer"] = answer
#    state["agent"] = agent
#    state["confidence"] = confidence
#    state["decision_source"] = decision_source
#    state["answer_source"] = answer_source
#    state["execution_time"] = round(time.time() - start, 2)
#
#    trace_obj = {
#    "agent": agent,
#    "action": trace_type
#    }
#
#    if extra:
#        trace_obj.update(extra)
#
#    state.setdefault("trace", []).append(trace_obj)
#
#    return state
#

# Allocation mapping


def detect_intent_llm(query, state, llm):
    memory = state.get("memory", [])
    profile = state.get("profile", {})

    # last 1–2 turns
    context = []
    for m in reversed(memory):
        if m.get("assistant"):
            context.append({
                "query": m.get("query"),
                "intent": m.get("intent")
            })
        if len(context) == 2:
            break

    context_text = "\n".join([
        f"- {c['query']} ({c['intent']})"
        for c in reversed(context)
    ])

    prompt = f"""You are a financial assistant.Determine the user's intent.
-------------------------
CONTEXT
-------------------------
Recent conversation:
{context_text}
User profile:
- Risk: {profile.get("risk")}
- Goal: {profile.get("goal")}
- Investment: {profile.get("investment_type")}
- Amount: {profile.get("amount")}

-------------------------
INTENTS
-------------------------
Return ONLY one:
- advice → general question
- allocation → portfolio / fund suggestion
- projection → returns / future value
- execution → proceed / go ahead
- modify → user updates profile (risk, goal, amount)
- news_invest → investing based on market/news
- general_news → news only

RULES (strict priority):
1. execution  
User wants to proceed/continue  
("yes", "go ahead", "start", "next step") → execution
2. modify  
User explicitly changes profile  
(risk, goal, amount, investment type) → modify
3. projection  
Asks about returns, growth, future value, inflation, or goal sufficiency → projection
4. advice  
- timing decisions (invest now vs wait)  
- vague preferences (safe, balanced, less risk)  
- incomplete inputs (only amount or unclear goal)  
- macro uncertainty (inflation, volatility, economy without clear allocation ask)  
→ advice
5. news_invest  
ONLY if user explicitly asks for investment decisions BASED ON  
market trends / economy / sector
- Must indicate dependency on external conditions  
  (e.g., "based on current market", "which sectors are good now")
- Generic mentions (inflation, volatility, uncertainty) → advice  
If personal profile context present → allocation
6. allocation  
If query contains conflicting constraints:
   (high return + low/zero risk, safety + high growth)
→ allocation
If ANY of below:
- user EXPLICITLY asks for:
  "allocate", "split", "portfolio", "mix", "funds"
-user asks HOW to invest AND provides ANY personal context:
   (risk OR goal)→ allocation
- OR allocation + projection combined
Otherwise → advice
7. general_news  
News only, no investment decision
8. advice
If query contains STRICT conflicting constraints:
   (high/guaranteed returns + zero/no risk)
→ allocation
If user expresses balanced preference:
   (good returns + low risk, safe + decent returns)
→ advice
-------------------------
USER QUERY
-------------------------
{query}
Answer ONLY one word."""

    res = llm.invoke(prompt)
    intent = res.content.strip().lower()

    valid = ["advice", "allocation", "projection", "execution", "modify", "news_invest", "general_news"]

    if intent not in valid:
        intent = "advice"

    return intent


def detect_agents_llm(query, state, intent, llm):
    profile = state.get("profile", {})

    
    prompt = f"""
You are a STRICT tool selector for a financial advisor system.

Return ONLY the exact agents required for the query.

Do NOT over-select agents.
Do NOT under-select agents.

Agents are NOT mutually exclusive.
If multiple independent signals exist, return ALL relevant agents.

--------------------------------------------------
INPUT
--------------------------------------------------
Query: {query}
Intent: {intent}

User Profile:
- Risk: {profile.get("risk")}
- Goal: {profile.get("goal")}
- Investment: {profile.get("investment_type")}
- Amount: {profile.get("amount")}

--------------------------------------------------
AVAILABLE AGENTS
--------------------------------------------------

- market_agent
  Use for:
  - stocks
  - companies
  - sectors
  - equities
  - investment products
  - investment choices
  - stock performance

- news_agent
  Use for:
  - economic conditions
  - inflation
  - recession
  - interest rates
  - macro trends
  - current market conditions
  - market uncertainty
  - timing decisions

- risk_agent
  Use for:
  - risk tolerance
  - uncertainty about risk
  - conflicting risk preferences
  - safety vs returns
  - investment suitability by risk profile

- rag_agent
  Use for:
  - explanations
  - reasoning
  - conceptual understanding
  - impact analysis

--------------------------------------------------
DECISION RULES
--------------------------------------------------

1. MARKET AGENT

Use market_agent when the query involves:
- stocks
- companies
- sectors
- equities
- investment products
- investment choices
- stock performance

Also use for:
- suitable investments
- where should I invest
- investments matching risk profile

Do NOT use for:
- generic allocation advice
- broad portfolio diversification
WITHOUT specific investment choices.

--------------------------------------------------

2. NEWS AGENT

Use news_agent for:
- economic uncertainty
- inflation
- recession
- macro trends
- market conditions
- timing decisions
- invest now vs later

Do NOT use news_agent when:
- trends/timing are only supporting context
AND
- the main task is stock/company selection.
Do NOT use news_agent for stock/company performance explanations
unless macro/economic conditions are explicitly mentioned.

--------------------------------------------------

3. RISK AGENT

Use risk_agent when:
- the user is uncertain about risk
- the query involves risk tolerance
- the user asks for investments matching risk profile
- the query discusses safety vs returns
- the user expresses conflicting preferences

Examples:
- high returns but low risk
- aggressive growth but safety

Do NOT use when:
- the user already specifies a stable risk profile
AND
- there is no uncertainty/conflict.
Always include risk_agent when the query explicitly mentions risk tolerance or risk profile.

--------------------------------------------------

4. RAG AGENT

Use rag_agent for:
- explanations
- reasoning
- conceptual understanding
- impact analysis
- tradeoff explanations
- comparison questions

Keywords:
- why
- explain
- reasoning
- how
- impact
- better than

Do NOT use rag_agent for:
- personal risk tolerance assessment
- uncertainty about risk appetite
- conflicting safety vs returns preferences
- understanding personal risk tolerance
- uncertainty about how much risk to take
- Queries about understanding personal risk tolerance
should use risk_agent only.
- Do NOT use rag_agent for practical risk-management guidance alone.

--------------------------------------------------

5. MULTI-AGENT RULE

If multiple independent signals exist,
return ALL relevant agents.

--------------------------------------------------

6. DEFAULT RULE

Return [] for:
- generic investment advice
- broad diversification questions
- allocation-only queries
WITHOUT:
- stock selection
- macro/timing discussion
- explanation requests
- risk confusion

--------------------------------------------------
FEW-SHOT EXAMPLES
--------------------------------------------------

Query: "Based on market trends and news, what investments suit my risk level?"
Output: ["market_agent", "news_agent", "risk_agent"]

Query: "Given economic uncertainty, explain how I should manage investment risk"
Output: ["risk_agent", "news_agent", "rag_agent"]

Query: "Explain which stocks suit my risk profile and why"
Output: ["market_agent", "risk_agent", "rag_agent"]

Query: "Considering my risk tolerance and current market conditions, where should I invest and why?"
Output: ["market_agent", "risk_agent", "news_agent", "rag_agent"]

Query: "Things look uncertain, how should I invest?"
Output: ["news_agent"]

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return ONLY valid JSON list format.

Examples:
[]
["market_agent"]
["market_agent", "news_agent"]

No explanation.
"""
    res = llm.invoke(prompt)

    try:
        agents = json.loads(res.content)
        if not isinstance(agents, list):
            agents = []
    except:
        agents = []

    return agents

def decide_mode(intent, profile):
    profile_complete = all([
        profile.get("risk"),
        profile.get("goal"),
        profile.get("investment_type")
    ])

    if not profile_complete:
        return "ask_missing"

    if intent == "projection":
        return "project"

    if intent == "execution":
        return "execute"

    if intent in ["allocation", "modify", "news_invest"]:
        return "suggest"

    return "advise"

def run_agents(agent_list, state):
    results = {}

    if "market_agent" in agent_list:
        results["market"] = market_agent(state)

    if "news_agent" in agent_list:
        results["news"] = news_agent(state)

    if "risk_agent" in agent_list:
        results["risk"] = risk_agent(state)

    if "rag_agent" in agent_list:
        results["rag"] = rag_agent(state)

    return results

def advisor_agent(state: AgentState) -> AgentState:
    start = time.time()
   
    profile = (state.get("profile") or {}).copy()
    memory = state.get("memory", [])
    #last_msg = memory[-1] if memory else {}
    #raw_query = last_msg.get("user", state.get("query", "")).strip()
    raw_query = state.get("query", "").strip()
    query = re.sub(r"[^\w\s%]", " ", raw_query).lower().strip()
    amount_match = re.search(r"\b\d{3,7}\b", query)
    user_alloc, unknown_assets = extract_user_allocation(query)
    llm = get_llm(temperature=0)
    last_stage = None


    if memory:
        for m in reversed(memory):
            if m.get("stage"):
                last_stage = m.get("stage")
                break

    # -------------------------
    # RESTORE SELECTED FUNDS
    # -------------------------

    for m in reversed(memory):
            funds = m.get("selected_funds")
            if funds:
                state["selected_funds"] = funds
                break
    
    # -------------------------
    # INTENT DETECTION (moved early)
    # -------------------------
    llm_intent = detect_intent_llm(query, state, llm)

    intent = llm_intent 

    agents = detect_agents_llm(query, state, intent, llm)

    stage = decide_mode(intent, profile)

    state["intent"] = intent
    state["stage"] = stage

    print("LLM Intent:", intent)

    # -------------------------
    # STAGE DETECTION (CRITICAL)
    # -------------------------

    if memory:
        for m in reversed(memory):
            last_profile = m.get("profile", {})
            if last_profile and any(last_profile.values()):
                for k, v in last_profile.items():
                    if not profile.get(k):
                        profile[k] = v
                break

    if not query.strip():
       return set_state(
            state,
            start,
            answer="Please enter a valid query.",
            agent="advisor_agent",
            confidence=0.5,
            decision_source="validation",
            answer_source="advisor",
            trace_action="invalid_input"
        )           

    state.setdefault("tools_used", [])
    state.setdefault("trace", [])
    


    
    age_match = re.search(r"\b([1-9][0-9])\b", query)
    if age_match:
        profile["age"] = age_match.group(1)
    
    RISK_OPTIONS = ["low", "medium", "high"]
    GOAL_OPTIONS = ["growth", "income"]
    INVESTMENT_OPTIONS = ["sip", "lump sum"]

    words = query.split()

    # ---- RISK ----
    for word in words:
        match = normalize_term(word, RISK_OPTIONS)
        if match:
            profile["risk"] = match
            break

    # ---- GOAL ----
    for word in words:
        match = normalize_term(word, GOAL_OPTIONS)
        if match:
            profile["goal"] = match
            break

    # ---- INVESTMENT ----
    for i in range(len(words)):
        phrase = words[i]

        # handle "lump sum"
        if i < len(words) - 1:
            phrase2 = words[i] + " " + words[i+1]
            match = normalize_term(phrase2, INVESTMENT_OPTIONS)
            if match:
                profile["investment_type"] = match
                break

        match = normalize_term(phrase, INVESTMENT_OPTIONS)
        if match:
            profile["investment_type"] = match
            break

    state["profile"] = profile

    # Then enrich from memory ONLY if missing
    risk = profile.get("risk")
    goal = profile.get("goal")
    investment = profile.get("investment_type")

    profile_complete = all([risk, goal, investment])


    # # 2. THEN compare
    #prev_profile = {}

    #if memory and len(memory) >= 2:
    #    prev_profile = memory[-2].get("profile", {})

    #is_profile_update = profile != prev_profile

    if amount_match:
        profile["amount"] = int(amount_match.group())

    # ADD THIS BLOCK HERE
    expected = state.get("expected_next_input")

    if expected == "risk" and profile.get("risk"):
        state.pop("expected_next_input", None)

    elif expected == "goal" and profile.get("goal"):
        state.pop("expected_next_input", None)

    elif expected == "investment_type" and profile.get("investment_type"):
        state.pop("expected_next_input", None)

    elif expected == "amount" and profile.get("amount"):
        state.pop("expected_next_input", None)  
    

    missing = []

    if not profile.get("risk"):
        missing.append("risk level (low / medium / high)")

    if not profile.get("goal"):
        missing.append("goal (growth / income)")

    if not profile.get("investment_type"):
        missing.append("investment type (SIP / lump sum)")


    

    answer = ""
    if user_alloc and not any([risk, goal, investment]):
        answer += "\n\n💡 Tip: Share your risk level or goal for more personalized advice."

    # -------------------------
    # NO INFO → ask everything
    # -------------------------
    if user_alloc and not any([profile.get("risk"), profile.get("goal"), profile.get("investment_type")]):
            pass


    is_suggestion = stage == "suggest"
    is_projection = stage == "project"
    is_execution = stage == "execute"


    print("is_projection ",is_projection)


    # -------------------------
    # PRIORITY: AMOUNT INTENT
    # -------------------------
   

    # -------------------------
    # EXECUTION DETECTION (AFTER suggestion)
    # -------------------------

    warning_msg = ""

    allocation_gap_msg = ""
    
    total_user = sum(user_alloc.values()) if user_alloc else 0
    
    # ✅ ADD HERE
    #state["intent"] = (
    #"execution" if is_execution
    #else "projection" if is_projection   
    #else "suggestion" if is_suggestion
    #else "advice"
    #)
    
    #state["stage"] = state["last_intent"]

    default_alloc = ALLOCATION_MAP.get(
    (risk, goal),
    {"equity": 40, "debt": 40, "gold": 20}
    )

    if user_alloc:
        if total_user > 100:
            return set_state(
                state,
                start,
                answer="Your allocation exceeds 100%. Please adjust.",
                agent="advisor_agent",
                confidence=0.9,
                decision_source="validation",
                answer_source="advisor",
                trace_action="invalid_allocation"
                )
        
        elif total_user == 100:
            # still allow constraints to rebalance
            final_alloc = user_alloc.copy()

        else:
            # ✅ PARTIAL → merge smartly
            final_alloc = merge_allocation(user_alloc, default_alloc)
    else:
        final_alloc = default_alloc
    
    # ✅ FINAL ALLOCATION DECIDED → NOW VALIDATE LIMITS
    if final_alloc:
        state["active_asset"] = max(final_alloc, key=final_alloc.get)
        state["allocation_sum"] = sum(final_alloc.values())
    # -------------------------
    # APPLY CAPS
    # -------------------------
    for asset, percent in final_alloc.items():
        if asset in MAX_LIMITS and percent > MAX_LIMITS[asset]:
            final_alloc[asset] = MAX_LIMITS[asset]
    # ✅ ADD HERE (right after caps)
    for asset, percent in user_alloc.items():
        if asset in MAX_LIMITS and percent > MAX_LIMITS[asset]:
            warning_msg += f"\n⚠️ {asset.capitalize()} capped at {MAX_LIMITS[asset]}% to reduce risk.\n"
    # -------------------------
    # ADD THIS BLOCK HERE (REDISTRIBUTION)
    # -------------------------
    
    # -------------------------
    # NORMALIZE AFTER CAPS (FINAL FIX)
    # -------------------------
    total = sum(final_alloc.values())

    if total < 100:
        remaining = 100 - total

        safe_assets = [k for k in final_alloc if k not in MAX_LIMITS]

        if safe_assets:
            share = remaining // len(safe_assets)

            for k in safe_assets:
                final_alloc[k] += share
    
    user_defined_partial = 0 < total_user < 100
    
    if user_defined_partial:
        remaining_assets = [k for k in final_alloc if k not in user_alloc]
    
        allocation_gap_msg += "\nRemaining allocation applied to:\n"
    
        for asset in remaining_assets:
            allocation_gap_msg += f"- {asset.capitalize()} → {final_alloc[asset]}%\n"
    
    # -------------------------
    # INVESTMENT AMOUNT
    # -------------------------
    
    amount = profile.get("amount")

    amount_block = ""
    
    if amount and risk and goal:

        if investment == "sip":
                amount_block = f"\n💰 Monthly SIP: ₹{amount:,}\n\n"
        elif investment == "lump sum":
            amount_block = f"\n💰 Lump Sum: ₹{amount:,}\n\n"
        else:
            amount_block = f"\n💰 Investment Amount: ₹{amount:,}\n\n"

        
        amount_block += "\n📊 Suggested split:\n\n"
       
        for asset, percent in final_alloc.items():
            fund_amount = int(amount * percent / 100)
    
            amount_block += f"- ₹{fund_amount:,} ({percent}%) → {asset.capitalize()}\n"
    
    if not amount:
        if investment == "sip":
            msg = "Before proceeding, please tell me your monthly investment amount (e.g., ₹5,000/month)."
        elif investment == "lump sum":
            msg = "Before proceeding, please tell me your one-time investment amount (e.g., ₹50,000)."
        else:
            msg = "Before proceeding, please tell me your investment amount (e.g., ₹5,000/month for SIP or ₹50,000 one-time)"

        return set_state(
            state,
            start,
            answer=msg,
            agent="advisor_agent",
            confidence=0.9,
            decision_source="clarification",
            answer_source="advisor",
            trace_action="missing_amount"
        )   
    
    if investment == "sip":
        sip_amount = f"₹{amount:,}/month" if amount else "₹5,000/month"
    elif investment == "lump sum":
        sip_amount = f"₹{amount:,} (one-time)" if amount else "₹50,000 (one-time)"
    else:
        sip_amount = "your investment amount"

    suggestion_block = ""

    if is_suggestion:

        # ✅ default fallback
        selected_funds = [
        "HDFC Balanced Advantage Fund",
        "ICICI Prudential Equity Savings Fund",
        "SBI Flexi Cap Fund"
        ]

        if risk and goal and investment:
            key = (risk, goal, investment)
            base_funds = FUND_SUGGESTIONS.get(key, [])
            if key in FUND_SUGGESTIONS:
                #selected_funds = FUND_SUGGESTIONS[key]
                seed = int(hashlib.md5(query.encode()).hexdigest(), 16)
                random.seed(seed)
                selected_funds = random.sample(base_funds, min(3, len(base_funds)))
                suggestion_block = "\n\n📊 Suggested funds:\n\n" + alloc(selected_funds)

            else:
                suggestion_block = "\n\n📊 Here are some good starting options:\n\n" + alloc(selected_funds)
        else:
            suggestion_block = "\n\n📊 Here are some good starting options:\n\n" + alloc(selected_funds) + \
            "\n\n💡 I can suggest better if you share:\n- Risk level\n- Goal\n- Investment type (SIP or lump sum)"

        state["selected_funds"] = selected_funds


    if not suggestion_block and not is_execution:
        suggestion_block = "\n\n💡 If you want, I can suggest specific funds tailored to your profile."

    # -------------------------
    # EXECUTION BLOCK (ONLY IF execution)
    # -------------------------
    execution_block = ""
    projection_block = ""

    if is_execution:
        
        # ------------------------- 
        # SIP PROJECTION
        # -------------------------
        return_map = {
        "low": 8,
        "medium": 10,
        "high": 12
        }

        rate = return_map.get(risk, 10)
        fv_10 = fv_15 = None
        projection_block = "\n\n📈 Future Value Projection:\n\n"
        if amount and investment == "sip":

            fv_10 = calculate_sip_future_value(amount, rate, 10)
            fv_15 = calculate_sip_future_value(amount, rate, 15)

            
            projection_block += f"- ₹{amount:,}/month → ₹{fv_10:,} in 10 years ({rate}% return)\n"
            projection_block += f"- ₹{amount:,}/month → ₹{fv_15:,} in 15 years ({rate}% return)\n"
        
        elif investment == "lump sum":

            fv_10 = calculate_lumpsum_future_value(amount, rate, 10)
            fv_15 = calculate_lumpsum_future_value(amount, rate, 15)

            projection_block += f"- ₹{amount:,} → ₹{fv_10:,} in 10 years ({rate}% return)\n"
            projection_block += f"- ₹{amount:,} → ₹{fv_15:,} in 15 years ({rate}% return)\n"

        # ✅ ONLY read from state
        selected_funds = state.get("selected_funds", [])

        if not selected_funds:
            return set_state(
            state,
                start,
                answer="Please ask for fund suggestions first.",
                agent="advisor_agent",
                confidence=0.5,
                decision_source="validation",
                answer_source="advisor",
                trace_action="missing_funds"
            )

        fund_split = []

        if selected_funds and amount:

            assets = list(final_alloc.keys())

            for i, fund in enumerate(selected_funds[:len(assets)]):
                asset = assets[i]
                percent = final_alloc[asset]

                fund_amount = int(amount * percent / 100)   # ✅ MOVE HERE

                fund_split.append(f"₹{fund_amount:,} ({percent}%) → {fund}")

        if fund_split:
            if investment == "sip":
                execution_block += "📊 Allocation split (monthly):\n"
            elif investment == "lump sum":
                execution_block += "📊 Investment allocation (one-time):\n"
            else:
                execution_block += "📊 Allocation:\n"

            execution_block += "\n".join(f"- {f}" for f in fund_split) + "\n"

        execution_block += "\n\n"

        execution_block += alloc([
            "1. Start investment via your broker/app (Groww, Zerodha, etc.)",
            "2. Enable auto-debit for SIP consistency" if investment == "sip" else "2. Invest the amount in one go via your broker/app",
            "3. Do not stop during market dips",
            "4. Review portfolio every 6–12 months"
            ])
    
    if stage == "project":

        return_map = {
        "low": 8,
        "medium": 10,
        "high": 12
        }

        rate = return_map.get(risk, 10)

        if investment == "sip":
            fv_10 = calculate_sip_future_value(amount, rate, 10)
            fv_15 = calculate_sip_future_value(amount, rate, 15)

            projection_block = f"""
📈 Future Value Projection:

₹{amount:,}/month → ₹{fv_10:,} in 10 years ({rate}% return)
₹{amount:,}/month → ₹{fv_15:,} in 15 years ({rate}% return)

👉 Say 'go ahead' to proceed.
"""

        elif investment == "lump sum":
            fv_10 = calculate_lumpsum_future_value(amount, rate, 10)
            fv_15 = calculate_lumpsum_future_value(amount, rate, 15)

            projection_block = f"""
📈 Future Value Projection:

₹{amount:,} → ₹{fv_10:,} in 10 years ({rate}% return)
₹{amount:,} → ₹{fv_15:,} in 15 years ({rate}% return)

👉 Say 'go ahead' to proceed.
"""

    profile_lines = []
    profile_section= ""
    # -------------------------
    # PROFILE EXTRACTION
    # -------------------------
    if profile:

        if profile.get("risk"):
           profile_lines.append(f"- Risk: {profile.get('risk')}")

        if profile.get("goal"):
            profile_lines.append(f"- Goal: {profile.get('goal')}")

        if profile.get("investment_type"):
            profile_lines.append(f"- Investment: {profile.get('investment_type').upper()}")

        profile_section = "\n".join(profile_lines) + "\n\n"

    # -------------------------
    # RUN AGENTS (CORRECT)
    # -------------------------
    agent_results = run_agents(agents, state.copy())

    # -------------------------
    # APPEND AGENT INSIGHTS (FINAL)
    # -------------------------


    if not user_alloc and unknown_assets and not amount_match:
        return set_state(
            state,
            start,
            answer=f"I couldn't recognize: {', '.join(unknown_assets)}.\nTry assets like equity, debt, gold, crypto.",
            agent="advisor_agent",
            confidence=0.5,
            decision_source="validation",
            answer_source="advisor",
            trace_action="invalid_input"
        )

        # ✅ If user gave NO useful info → ask
    if len(missing) >= 2 and not user_alloc:
        followup = "\n\nTo refine this further, you can also share:\n"
        followup += "\n".join([f"- {m}" for m in missing])

        answer = f"""Got it — I can help with that.

{followup}

Can you share that?
"""
        return set_state(
            state,
            start,
            answer=answer,
            agent="advisor_agent",
            confidence=0.9,
            decision_source="clarification",
            answer_source="advisor",
            trace_action="ask_missing"
        )

    intro = ""
    if is_projection:
        intro = "Here’s how your investment can grow over time:"
    elif is_execution:
        intro = "Great — here’s how you can proceed:"
    elif is_suggestion:
        intro = "Here’s a plan based on your profile:"
    else:
        intro = "Got it — based on what you've shared:"
    
    answer = f"""{intro}

{profile_section}

📌 Recommended approach:

- Balanced allocation based on your risk profile
- Diversification across asset classes
- Continue disciplined investing

💡 Suggested allocation:

{alloc([f"{k.capitalize()} → {v}%" for k, v in final_alloc.items()])}

{amount_block}

{suggestion_block}

{projection_block if is_projection else ""}

{execution_block if is_execution else ""}
"""

    if agent_results.get("market"):
        answer += "\n\n📊 Market Insights:\n" + agent_results["market"]

    if agent_results.get("news"):
        answer += "\n\n📰 Latest Trends:\n" + agent_results["news"]

    if agent_results.get("risk"):
        answer += "\n\n⚠️ Risk Insight:\n" + agent_results["risk"]

    if agent_results.get("rag"):
        answer += "\n\n📘 Additional Info:\n" + agent_results["rag"]

    extra={
    "tools_used": agents,
    "advisor_allocation": final_alloc
    }

    return set_state(
    state,
    start,
    answer=answer,
    agent="advisor_agent",
    confidence=0.85,
    decision_source="advisor_reasoning",
    answer_source="advisor",
    trace_action="orchestration",
    extra=extra   # ✅ ADD THIS
)