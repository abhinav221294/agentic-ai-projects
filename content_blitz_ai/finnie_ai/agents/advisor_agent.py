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
from utils.format_utils import (alloc,extract_amount,extract_rate,
extract_projection_duration, extract_age)
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


def detect_remaining_intent(query, state, llm):

    memory = state.get("memory", [])
    profile = state.get("profile", {})

    # =====================================================
    # RECENT CONTEXT
    # =====================================================

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

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""You are a STRICT financial intent classifier.

Your task:
Return ONLY the single best intent.

No explanation.
No sentence.
Only one word.

--------------------------------------------------
IMPORTANT
--------------------------------------------------

execution, modify, and projection intents
have ALREADY been handled earlier.

DO NOT return:
- execution
- modify
- projection

--------------------------------------------------
CONTEXT
--------------------------------------------------

Recent conversation:
{context_text}

User profile:
- Risk: {profile.get("risk")}
- Goal: {profile.get("goal")}
- Investment: {profile.get("investment_type")}
- Amount: {profile.get("amount")}

--------------------------------------------------
VALID INTENTS
--------------------------------------------------

- advice
  General financial guidance

- allocation
  Portfolio allocation / investment suggestions

- news_invest
  Investment decisions based on market/economy/news

- general_news
  News or market information only

--------------------------------------------------
DECISION RULES
--------------------------------------------------

IMPORTANT:
Apply rules TOP TO BOTTOM.
Use FIRST matching rule only.

--------------------------------------------------
1. NEWS_INVEST
--------------------------------------------------

ONLY return news_invest if the query EXPLICITLY mentions:
- market
- economy
- inflation
- trends
- sectors
- interest rates
- news
- macro conditions

AND user asks:
- where should I invest
- what sectors are good
- what investments are best now

Examples:
- where should I invest based on current market
- best sectors during inflation
- what investments suit current economy

Return: news_invest

IMPORTANT:
If query is ONLY asking about news/info
WITHOUT investment decision:
DO NOT use news_invest.

--------------------------------------------------
2. GENERAL_NEWS
--------------------------------------------------

Return general_news IF:
query asks ONLY about:
- market news
- economy
- inflation
- sectors
- trends
- stocks/news updates

WITHOUT asking for investment advice.

Examples:
- how is the market doing
- latest AI stock trends
- what is happening in tech sector

Return: general_news

--------------------------------------------------
3. ALLOCATION
--------------------------------------------------

Return allocation IF:
user asks:
- how to invest
- portfolio suggestion
- fund recommendation
- allocation strategy
- diversification
- asset split

OR user provides:
- risk
- goal
- investment preference

AND wants investment suggestions.

Examples:
- suggest portfolio
- where should I invest
- recommend funds
- diversify my investments
- medium risk investment plan

Return: allocation

--------------------------------------------------
4. ADVICE
--------------------------------------------------

Return advice for:
- vague financial concerns
- balanced/safe preferences
- timing uncertainty
- incomplete information
- general guidance

Examples:
- should I invest now or wait
- I want safety and returns
- markets look uncertain
- I am confused about investing

Return: advice

--------------------------------------------------
SPECIAL RULES
--------------------------------------------------

STRICT conflicting constraints:
- guaranteed high returns
- zero risk high growth
- double money safely quickly

→ allocation

Balanced preference:
- safe and decent returns
- good returns with low risk

→ advice

Single-word followups:
- use conversation context

Examples:
- growth
- SIP

--------------------------------------------------
USER QUERY
--------------------------------------------------

{query}

Return ONLY one intent word."""

    # =====================================================
    # LLM CALL
    # =====================================================

    res = llm.invoke(prompt)

    intent = res.content.strip().lower()

    market_terms = [
    "market",
    "economy",
    "inflation",
    "sector",
    "trend",
    "interest rate",
    "news",
    "macro"
    ]

    if (
        intent == "news_invest"
        and not any(t in query.lower() for t in market_terms)
    ):
        intent = "allocation"

    # =====================================================
    # VALIDATION
    # =====================================================

    valid = [
        "advice",
        "allocation",
        "news_invest",
        "general_news"
    ]

    if intent not in valid:
        intent = "advice"

    return intent


def detect_intent_llm(query, state, llm):

    """
    Hierarchical Intent Detection

    STAGE 1:
    - execution
    - modify
    - other

    STAGE 2:
    - projection
    - non_projection

    STAGE 3:
    - allocation
    - advice
    - news_invest
    - general_news
    """

    memory = state.get("memory", [])
    profile = state.get("profile", {})

    # =====================================================
    # RECENT CONTEXT
    # =====================================================

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

    # =====================================================
    # STAGE 1
    # ACTION INTENTS
    # =====================================================

    stage1_prompt = f"""
You are a STRICT financial intent classifier.

Your task:
Return ONLY one word.

VALID OUTPUTS:
- execution
- modify
- other

--------------------------------------------------
DEFINITIONS
--------------------------------------------------

execution:
User wants to proceed/start/continue.

Examples:
- yes
- go ahead
- continue
- proceed
- start investment
- next step

modify:
User explicitly changes:
- amount
- risk
- goal
- investment type
- allocation preference

Examples:
- increase SIP
- change risk
- switch to lump sum
- reduce equity

other:
Anything else.

--------------------------------------------------
CONTEXT
--------------------------------------------------

Recent conversation:
{context_text}

User Query:
{query}

Return ONLY one word.
"""

    res1 = llm.invoke(stage1_prompt)

    stage1_intent = res1.content.strip().lower()

    if stage1_intent in ["execution", "modify"]:

        print("LLM Intent:", stage1_intent)

        return stage1_intent

    # =====================================================
    # STAGE 2
    # PROJECTION DETECTION
    # =====================================================

    stage2_prompt = f"""
You are a STRICT financial projection classifier.

Your task:
Determine whether the user is asking about:
- future value
- returns
- wealth growth
- corpus estimation
- long-term investment growth

VALID OUTPUTS:
- projection
- non_projection

--------------------------------------------------
PROJECTION EXAMPLES
--------------------------------------------------

- what returns can I expect
- how much wealth can I create
- future value in 10 years
- retirement corpus
- what will this grow to
- can I reach 5 crore

--------------------------------------------------
NON-PROJECTION EXAMPLES
--------------------------------------------------

- suggest portfolio
- where should I invest
- should I invest now
- market news today
- change risk profile

--------------------------------------------------
CONTEXT
--------------------------------------------------

Recent conversation:
{context_text}

User Query:
{query}

Return ONLY one word.
"""

    res2 = llm.invoke(stage2_prompt)

    stage2_intent = res2.content.strip().lower()

    if stage2_intent == "projection":

        print("LLM Intent:", "projection")

        return "projection"

    # =====================================================
    # STAGE 3
    # REMAINING INTENTS
    # =====================================================

    intent = detect_remaining_intent(
        query=query,
        state=state,
        llm=llm
    )

    print("LLM Intent:", intent)

    return intent


def detect_agents_llm(query, state, intent, llm):
    profile = state.get("profile", {})

    
    prompt = f"""You are a STRICT tool selector for a financial advisor system.

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

No explanation."""
    
    res = llm.invoke(prompt)

    try:
        agents = json.loads(res.content)
        if not isinstance(agents, list):
            agents = []
    except:
        agents = []

    return agents

def decide_mode(intent, profile_complete):

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
        market_result = market_agent(state)

        if isinstance(market_result, dict):
            results["market"] = market_result.get("answer", "")
        else:
            results["market"] = str(market_result)

    if "news_agent" in agent_list:
        news_result = news_agent(state)

        if isinstance(news_result, dict):
            results["news"] = news_result.get("answer", "")
        else:
            results["news"] = str(news_result)

    if "risk_agent" in agent_list:
        risk_result = risk_agent(state)

        if isinstance(risk_result, dict):
            results["risk"] = risk_result.get("answer", "")
        else:
            results["risk"] = str(risk_result)

    if "rag_agent" in agent_list:
        rag_result = rag_agent(state)

        if isinstance(rag_result, dict):
            results["rag"] = rag_result.get("answer", "")
        else:
            results["rag"] = str(rag_result)

    return results
def advisor_agent(state: AgentState) -> AgentState:
    start = time.time()
   
    profile = (state.get("profile") or {}).copy()
    memory = state.get("memory", [])
    #last_msg = memory[-1] if memory else {}
    #raw_query = last_msg.get("user", state.get("query", "")).strip()
    raw_query = state.get("query", "").strip()
    clean_query = re.sub(r"[^\w\s%,₹.-]", " ", raw_query).lower().strip()
    amount_match = extract_amount(query=raw_query)
    query = clean_query
    user_alloc, unknown_assets = extract_user_allocation(query)
    llm = get_llm(temperature=0)


    # -------------------------
    # RESTORE SELECTED FUNDS
    # -------------------------

    for m in reversed(memory):
            funds = m.get("selected_funds")
            if funds:
                state["selected_funds"] = funds
                break
    

    # -------------------------
    # STAGE DETECTION (CRITICAL)
    # -------------------------

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
    expected = state.get("expected_next_input")

    # Then enrich from memory ONLY if missing
    
    state["profile"] = profile

    age = extract_age(query)

    print("age : ", age)

    if age:
        profile["age"] = age
    
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



    # # 2. THEN compare
    #prev_profile = {}

    #if memory and len(memory) >= 2:
    #    prev_profile = memory[-2].get("profile", {})

    #is_profile_update = profile != prev_profile

    if amount_match and (
        expected == "amount"
        or "amount" in query
        or "invest" in query
        or "sip" in query
    ):
        profile["amount"] = float(amount_match)

    
    print("amount_match ", amount_match)

    state["profile"] = profile

    
    # -------------------------
    # FUND SUGGESTION DETECTION
    # -------------------------

    query_lower = query.lower().strip()

    fund_keywords = [
    "fund",
    "funds",
    "mutual fund",
    "mutual funds",
    "portfolio",
    "investment option",
    "investment options"
    ]

    fund_confirmation_words = [
    "please suggest",
    "suggest funds",
    "recommend funds",
    "give funds",
    "show funds",
    "fund suggestions"
    ]


    # -------------------------
    # INTENT DETECTION (moved early)
    # -------------------------

    

    risk_phrases = {

    # =========================
    # High leaning
    # =========================

    "medium to high": "high",
    "medium-to-high": "high",
    "moderate to high": "high",
    "medium high": "high",

    "aggressive growth": "high",
    "very aggressive": "high",
    "high growth": "high",
    "maximum returns": "high",

    # =========================
    # Medium leaning
    # =========================

    "low to medium": "medium",
    "low-to-medium": "medium",

    "balanced": "medium",
    "balanced strategy": "medium",
    "balanced investment": "medium",

    "moderate": "medium",

    "avoid high risk": "medium",
    "avoid extremely high risk": "medium",

    "market volatility": "medium",
    "economic slowdown": "medium",

    "controlled risk": "medium",
    "stable growth": "medium",

    # =========================
    # Explicit
    # =========================

    "high risk": "high",
    "medium risk": "medium",
    "low risk": "low"
    }

    

    for phrase, mapped in risk_phrases.items():

        if phrase in query:
            profile["risk"] = mapped
            break
        
    risk = profile.get("risk")        
    goal = profile.get("goal")
    investment = profile.get("investment_type")
    amount = profile.get("amount")

    profile_complete = (
    risk is not None
    and goal is not None
    and investment is not None
    and amount is not None
    )

    user_requested_funds = (
        profile_complete
        and (
        any(k in query_lower for k in fund_keywords)
        or any(w in query_lower for w in fund_confirmation_words)
        )
        )
    
    print("user_requested_funds ",user_requested_funds)

    remaining_missing = []

    if not profile.get("risk"):
        remaining_missing.append("risk")

    if not profile.get("goal"):
        remaining_missing.append("goal")

    if not profile.get("investment_type"):
        remaining_missing.append("investment_type")

    if profile.get("amount") is None:
        remaining_missing.append("amount")

    stage = None

    fund_confirmation = (
    any(k in query_lower for k in fund_keywords)
    or any(w in query_lower for w in fund_confirmation_words)
    )

    # continuation after advisor suggested funds
    last_assistant = ""

    # Skip current user turn
    for m in reversed(memory[:-1]):

        assistant_msg = m.get("assistant")

        if assistant_msg:
            last_assistant = assistant_msg.lower()
            break

    print("last_assistant:", last_assistant)
    

    if (
    query_lower in ["yes", "yeah", "yup", "sure", "ok", "okay"]
    and "suggest" in last_assistant
    and "fund" in last_assistant
    ):
        fund_confirmation = True

    if fund_confirmation:
        user_requested_funds = True

   # -------------------------
    # FUND CONFIRMATION OVERRIDE
    # -------------------------

    if fund_confirmation and profile_complete:

        # User confirmed they want fund suggestions
        # Example:
        # Assistant: "I can also suggest funds"
        # User: "yes"

        intent = "allocation"
        stage = "suggest"
        user_requested_funds = True

    else:

        llm_intent = detect_intent_llm(query, state, llm)
        intent = llm_intent

        # Pure allocation flow does not need external agents


    # -------------------------
    # AGENT DETECTION
    # -------------------------

    # Pure onboarding / allocation flow
    # should NOT trigger external agents

    onboarding_active = (
        expected is not None
        or (
        intent == "allocation"
        and profile_complete
        and not user_requested_funds
        )
        )

    if onboarding_active:

        agents = []

    else:

        agents = detect_agents_llm(
        query=query,
        state=state,
        intent=intent,
        llm=llm
        )

    if not stage:
        stage = decide_mode(intent, profile_complete)   

    state["intent"] = intent
    state["stage"] = stage

    print("LLM Intent:", intent)

    # -------------------------
    # CONTINUATION CLEANUP
    # -------------------------

    completed = {
    "risk": profile.get("risk"),
    "goal": profile.get("goal"),
    "investment_type": profile.get("investment_type"),
    "amount": profile.get("amount")
    }

    if expected and completed.get(expected):

        # If investment type AND amount came together
        # clear everything properly
        state.pop("expected_next_input", None)


    # -------------------------
    # CONTINUATION STATE
    # -------------------------

    if remaining_missing:
        state["expected_next_input"] = remaining_missing[0]
    else:
        state.pop("expected_next_input", None)

    #expected = state.get("expected_next_input")


    

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


    print("is_suggestion ",is_suggestion)
    print("is_projection ",is_projection)
    print("is_execution ",is_execution)

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
    # PROFILE COMPLETION FLOW
    # -------------------------



    missing_non_amount = [
        x for x in remaining_missing
        if x != "amount"
        ]   
    
    if missing_non_amount:

        questions = []

        if "risk" in missing_non_amount:
            questions.append(
            "• Risk level: Low / Medium / High"
            )

        if "goal" in missing_non_amount:
            questions.append(
            "• Goal: Growth / Income"
            )

        if "investment_type" in missing_non_amount:
            questions.append(
            "• Investment type: SIP / Lump sum"
            )

        state["expected_next_input"] = missing_non_amount[0]

        return set_state(
            state,
            start,
            answer=(
                "Before suggesting investments, please share:\n\n"
                + "\n".join(f"- {q}" for q in questions)
            ),
            agent="advisor_agent",
            confidence=0.95,
            decision_source="clarification",
            answer_source="advisor",
            trace_action="missing_profile"
            )

    if (
        not missing_non_amount
        and profile.get("amount") is None
        ):

        investment_type = profile.get("investment_type")

        if investment_type == "sip":

            message = (
            "Before proceeding, please tell me your "
            "monthly investment amount "
            "(e.g., ₹5,000/month)."
        )

        elif investment_type == "lump sum":

            message = (
            "Before proceeding, please tell me your "
            "one-time investment amount "
            "(e.g., ₹50,000)."
        )

        else:

            message = (
            "Before proceeding, please tell me your "
            "investment amount."
            )

        state["expected_next_input"] = "amount"

        return set_state(
        state,
        start,
        answer=message,
        agent="advisor_agent",
        confidence=0.95,
        decision_source="clarification",
        answer_source="advisor",
        trace_action="missing_amount"
    )           

    # -------------------------
    # FUND SUGGESTIONS
    # -------------------------

    suggestion_block = "" 

    if is_suggestion and user_requested_funds:

        # default fallback
        selected_funds = [
        "HDFC Balanced Advantage Fund",
        "ICICI Prudential Equity Savings Fund",
        "SBI Flexi Cap Fund"
        ]

        if risk and goal and investment:

            key = (risk, goal, investment)

            base_funds = FUND_SUGGESTIONS.get(key, [])

            if key in FUND_SUGGESTIONS and base_funds:

                seed = int(hashlib.md5(query.encode()).hexdigest(), 16)

                random.seed(seed)

                selected_funds = random.sample(
                base_funds,
                min(3, len(base_funds))
                )

                suggestion_block = (
                "\n\n📊 Suggested funds:\n\n"
                + alloc(selected_funds))
                
            else:

                suggestion_block = (
                "\n\n📊 Here are some good starting options:\n\n"
                + alloc(selected_funds)
                )

        else:

            suggestion_block = (
            "\n\n📊 Here are some good starting options:\n\n"
            + alloc(selected_funds)
            + "\n\n💡 I can suggest better if you share:"
            "\n- Risk level"
            "\n- Goal"
            "\n- Investment type (SIP or lump sum)"
            )

        state["selected_funds"] = selected_funds

    # -------------------------
    # NO FUND REQUEST YET
    # -------------------------

    elif is_suggestion and not is_execution:

        suggestion_block = (
        "\n\n💡 If you'd like, I can also suggest "
        "specific funds tailored to your profile."
        )


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

        rate = profile.get("expected_return")
        # 2. Extract from query if not already stored
        if not rate:

            extracted_rate = extract_rate(query)

            if extracted_rate:
                rate = extracted_rate
                profile["expected_return"] = rate

            # 3. Fallback to risk-based defaults
            if not rate:
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
    
    if stage == "project" and is_projection:

        return_map = {
        "low": 8,
        "medium": 10,
        "high": 12
        }

        rate = return_map.get(risk, 10)

        projection_info = extract_projection_duration(query)

        projection_block = "\n📈 Future Value Projection:\n"

        # -------------------------
        # CUSTOM DURATION
        # -------------------------

        if projection_info["custom"]:

            years = projection_info["years"]
            years = min(years, 50)

            if investment == "sip":

                future_value = calculate_sip_future_value(
                amount,
                rate,
                years
                )

            else:

                future_value = calculate_lumpsum_future_value(
                amount,
                rate,
                years
                )

            # display formatting
            if years >= 1:

                duration_label = (
                    f"{years:.1f} years"
                        if years % 1 != 0
                        else f"{int(years)} years"
                            )

            else:

                months = max(round(years * 12), 1)

                duration_label = f"{months} months"

            if investment == "sip":

                projection_block += (
                f"\n₹{amount:,.0f}/month "
                f"→ ₹{future_value:,.0f} "
                f"in {duration_label} "
                f"({rate}% return)\n"
                )

            else:

                projection_block += (
                f"\n₹{amount:,.0f} "
                f"→ ₹{future_value:,.0f} "
                f"in {duration_label} "
                f"({rate}% return)\n"
                )

        # -------------------------
        # DEFAULT PROJECTIONS
        # -------------------------

        else:

            default_years = [10, 15]

            for years in default_years:

                if investment == "sip":

                    future_value = calculate_sip_future_value(
                    amount,
                    rate,
                    years
                    )

                    projection_block += (
                    f"\n₹{amount:,.0f}/month "
                    f"→ ₹{future_value:,.0f} "
                    f"in {years} years "
                    f"({rate}% return)\n"
                    )

                else:

                    future_value = calculate_lumpsum_future_value(
                    amount,
                    rate,
                    years
                    )

                    projection_block += (
                    f"\n₹{amount:,.0f} "
                    f"→ ₹{future_value:,.0f} "
                    f"in {years} years "
                    f"({rate}% return)\n"
                    )

        projection_block += "\n👉 Say 'go ahead' to proceed.\n"

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

            investment_type = profile.get("investment_type").lower()

            investment_display_map = {
            "sip": "SIP",
            "lump sum": "Lump Sum"
            }

            investment_display = investment_display_map.get(
            investment_type,
            investment_type
            )

            profile_lines.append(
            f"- Investment: {investment_display}"
            )

        profile_section = "\n".join(profile_lines) + "\n\n"

    
    # -------------------------
    # AMOUNT BLOCK
    # -------------------------

    amount_block = ""

    if amount:
        if investment == "sip":
            amount_block = f"💰 Monthly SIP: ₹{amount:,.0f}\n"
        elif investment == "lump sum":

            amount_block = f"💰 Lump Sum: ₹{amount:,.0f}\n"
        else:
            amount_block = f"💰 Investment Amount: ₹{amount:,.0f}\n"

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