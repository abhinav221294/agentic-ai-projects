from utils.state import AgentState
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent
import re
import time
from difflib import get_close_matches
from utils.llm import get_llm

# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
#def _set(state, start, answer, agent, confidence, decision_source, answer_source, trace_type, extra=None):
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
ALLOCATION_MAP = {

    # LOW RISK
    ("low", "income"): {
    "equity": 30,
    "debt": 50,
    "gold": 20},
    

    ("low", "growth"): {
    "equity": 30,
    "debt": 50,
    "gold": 20
    }, 
 
    # MEDIUM
    ("medium", "income"): {
    "equity": 40,
    "debt": 40,
    "gold": 20},

    ("medium", "growth"):
     {"equity": 60,
    "debt": 25,
    "gold": 15},

    # HIGH RISK
    ("high", "income"): {
    "equity": 70,
    "debt": 20,
    "gold": 10},

    ("high", "growth"): {
    "equity": 80,
    "debt": 15,
    "gold": 5}
    }


ASSET_MAP = {
    "equity": ["equity", "stocks", "shares", "mutual fund", "mutual funds", "mf"],
    "debt": ["debt", "bonds", "fixed income"],
    "gold": ["gold"],
    "crypto": ["crypto", "bitcoin", "ethereum"],
    "real_estate": ["real estate", "property"],
}

MAX_LIMITS = {
    "crypto": 20,
    "gold": 30
}


def _set(state, start, answer, agent, confidence, decision_source, answer_source, trace_type, extra=None, add_trace=True):
    state["answer"] = answer
    state["agent"] = agent
    state["confidence"] = confidence
    state["decision_source"] = decision_source
    state["answer_source"] = answer_source
    state["execution_time"] = round(time.time() - start, 2)
    
    state["profile"] = state.get("profile", {})

    # ✅ Only add trace if allowed
    if add_trace:
        trace_obj = {
            "agent": agent,
            "action": trace_type
        }

        if extra:
            trace_obj.update(extra)
        state.setdefault("trace", []).append(trace_obj)
    return state

def alloc(lines):
    return "\n".join(lines)

def calculate_sip_future_value(monthly_investment, annual_return=10, years=10):
    """
    Calculate future value of SIP
    """
    r = annual_return / 100 / 12   # monthly rate
    n = years * 12

    fv = monthly_investment * (((1 + r)**n - 1) / r) * (1 + r)
    return int(fv)

def calculate_lumpsum_future_value(principal, annual_return=10, years=10):
    r = annual_return / 100
    fv = principal * ((1 + r) ** years)
    return int(fv)


def extract_user_allocation(query):
    allocation = {}
    unknown_assets = []

    query = query.lower()

    # ✅ support both formats
    pattern1 = r"(\d+)%?\s*([a-zA-Z ]+)"   # 100 crypto / 100% crypto
    pattern2 = r"([a-zA-Z ]+)\s*(\d+)%?"   # crypto 100 / crypto 100%

    matches1 = re.findall(pattern1, query)
    matches2 = re.findall(pattern2, query)

    def map_asset(asset_raw, percent):
        asset_raw = asset_raw.strip().lower()
        percent = int(percent)

        for canonical, aliases in ASSET_MAP.items():
            all_terms = aliases + [canonical]

            match = get_close_matches(asset_raw, all_terms, n=1, cutoff=0.7)

            if match:
                allocation[canonical] = allocation.get(canonical, 0) + percent
                return True
        return False

    # format: 100 crypto
    for percent, asset in matches1:
        if not map_asset(asset, percent):
            unknown_assets.append(asset.strip())

    # format: crypto 100
    for asset, percent in matches2:
        if not map_asset(asset, percent):
            unknown_assets.append(asset.strip())

    # remove duplicates
    unknown_assets = list(set(unknown_assets))

    print("QUERY: ", query)
    print("MATCHES 1: ", matches1)
    print("MATCHES 2: ", matches2)
    print("USER_ALLOC: ", allocation)

    return allocation, unknown_assets


def merge_allocation(user_alloc, default_alloc):
    result = {}

    total_user = sum(user_alloc.values())
    remaining = 100 - total_user

    # ❌ invalid case
    if remaining < 0:
        return None

    # assets not provided by user
    remaining_assets = [k for k in default_alloc if k not in user_alloc]

    default_remaining_sum = sum(default_alloc[k] for k in remaining_assets)

    # ⚠️ edge case: user defined everything
    if default_remaining_sum == 0:
        return user_alloc

    # distribute remaining %
    for asset in default_alloc:
        if asset in user_alloc:
            result[asset] = user_alloc[asset]
        else:
            weight = default_alloc[asset] / default_remaining_sum
            result[asset] = round(weight * remaining)

    # include extra assets (like crypto)
    for asset in user_alloc:
        if asset not in result:
            result[asset] = user_alloc[asset]

    # ✅ normalize to 100
    total = sum(result.values())

    if total != 100:
        diff = 100 - total

        for k in result:
            if k not in MAX_LIMITS:
                result[k] += diff
                break

    return result

def extract_profile_llm(query, llm):

    prompt = f"""
Extract the user's financial profile from the text.

Return ONLY JSON with keys:
- risk (low / medium / high or null)
- goal (growth / income or null)
- investment_type (sip / lump sum or null)

Text:
{query}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        import json
        return json.loads(content)

    except Exception:
        return {}
    
def detect_intent_llm(query, llm):

    prompt = f"""
Classify the user's intent.

Return ONLY one of:
- advice
- allocation
- execution
- news_invest
- general_news

Query:
{query}
"""

    try:
        res = llm.invoke(prompt)
        intent = res.content.strip().lower()
        return intent
    except:
        return "advice"

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

    intent = detect_intent_llm(state["query"], llm)

    state["intent"] = intent
    
    llm = get_llm(temperature=0)

    profile_llm = extract_profile_llm(query, llm)

    profile.update({
    "risk": profile_llm.get("risk") or profile.get("risk"),
    "goal": profile_llm.get("goal") or profile.get("goal"),
    "investment_type": profile_llm.get("investment_type") or profile.get("investment_type")
    })

    # -------------------------
    # STAGE DETECTION (CRITICAL)
    # -------------------------
    last_stage = None

    if memory and len(memory) >= 2:
        last_stage = memory[-2].get("stage")
  

    #print("advisor memory ", memory)
    #print("profile memory ", profile)
    # 🔥 ALWAYS get last VALID profile
    # 🔥 ALWAYS fetch last valid profile

    if memory:
        for m in reversed(memory):
            last_profile = m.get("profile", {})
            if last_profile and any(last_profile.values()):
                for k, v in last_profile.items():
                    if not profile.get(k):
                        profile[k] = v

    if not query.strip():
       return _set(
        state, start,
        "Please enter a valid query.",
        "advisor_agent",
        0.5,
        "validation",
        "advisor",
        "invalid_input"
        )

    state.setdefault("tools_used", [])
    state.setdefault("trace", [])
    

    # -------------------------
    # INTENT DETECTION (moved early)
    # -------------------------
    is_decision = (
    "returns" in query or
    any(p in query for p in [
        "should", "invest", "what to do", "worth",
        "buy", "sell", "start", "choose"
        ]))
    
    age_match = re.search(r"\b([1-9][0-9])\b", query)
    if age_match:
        profile["age"] = age_match.group(1)

    if re.search(r"\blow\b.*\brisk\b|\brisk\b.*\blow\b", query):
        profile["risk"] = "low"

    elif re.search(r"\bmedium\b.*\brisk\b|\brisk\b.*\bmedium\b", query):
        profile["risk"] = "medium"

    elif re.search(r"\bhigh\b.*\brisk\b|\brisk\b.*\bhigh\b", query):
        profile["risk"] = "high"

    if "income" in query:
        profile["goal"] = "income"
    elif "growth" in query:
        profile["goal"] = "growth"

    if "sip" in query:
        profile["investment_type"] = "sip"
    elif "lump sum" in query or "lumpsum" in query:
        profile["investment_type"] = "lump sum"

    state["profile"] = profile
    #print(f"[PROFILE AFTER UPDATE] {profile}")

    # Then enrich from memory ONLY if missing
    risk = profile.get("risk")
    goal = profile.get("goal")
    investment = profile.get("investment_type")

     # 2. THEN compare
    prev_profile = {}

    if memory and len(memory) >= 2:
        prev_profile = memory[-2].get("profile", {})

    is_profile_update = profile != prev_profile

    if amount_match:
        profile["amount"] = int(amount_match.group())

    # -------------------------
    # PRIORITY: AMOUNT INTENT
    # -------------------------
    if amount_match and (profile.get("risk") and profile.get("goal")):
        is_execution = True

    # ✅ ADD THIS BLOCK HERE
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


    if not user_alloc and unknown_assets and not amount_match:
        return _set(
                state, start,
               f"I couldn't recognize: {', '.join(unknown_assets)}.\n"
                "Try assets like equity, debt, gold, crypto.\n"
                "Or did you mean something else?",
                "advisor_agent",
                0.8,
                "validation",
                "advisor",
                "invalid_asset"
                )

    # ✅ If user gave NO useful info → ask
    if len(missing) >= 2 and not user_alloc:
        followup = "\n\nTo refine this further, you can also share:\n"
        followup += "\n".join([f"- {m}" for m in missing])

        answer = f"""
Got it — I can help with that.

{followup}

Can you share that?
"""
        return _set(
        state, start,
        answer,
        "advisor_agent",
        0.9,
        "clarification",
        "advisor",
        "ask_missing"
    )

    answer = ""
    if user_alloc and not any([risk, goal, investment]):
        answer += "\n\n💡 Tip: Share your risk level or goal for more personalized advice."

    # -------------------------
    # NO INFO → ask everything
    # -------------------------
    if user_alloc and not any([profile.get("risk"), profile.get("goal"), profile.get("investment_type")]):
            pass

    
    # -------------------------
    # FOLLOW-UP INTENT
    # -------------------------

    suggestion_block = ""

    already_suggested = False

    if memory and len(memory) >= 2:
        last_answer = (memory[-2].get("assistant") or "").lower()
        if "📊 suggested funds" in last_answer:
            already_suggested = True


    # -------------------------
    # SUGGESTION DETECTION FIRST
    # -------------------------
    is_suggestion = False

    if profile.get("risk") and profile.get("goal"):

        # 1️⃣ Explicit ask
        if any(word in query for word in ["suggest", "recommend", "fund"]):
            is_suggestion = True

        # 2️⃣ Short follow-up
        elif (
        len(query.split()) <= 6
        and profile.get("investment_type")
        and not already_suggested
        ):
            is_suggestion = True

        # 3️⃣ Previous assistant hint
        elif not already_suggested and memory and len(memory) >= 2:
            last_answer = (memory[-2].get("assistant") or "").lower()

            if "suggest specific funds" in last_answer:
                is_suggestion = True

    # -------------------------
    # EXECUTION DETECTION (AFTER suggestion)
    # -------------------------
    is_execution = False
    warning_msg = ""
    if last_stage == "suggestion" and not is_decision and not is_profile_update:
        is_execution = True
    
    allocation_gap_msg = ""
    
    total_user = sum(user_alloc.values()) if user_alloc else 0
    
    # ✅ ADD HERE
    state["last_intent"] = (
        "execution" if is_execution
        else "suggestion" if is_suggestion
        else "advice"
        )
    
    state["stage"] = state["last_intent"]

    default_alloc = ALLOCATION_MAP.get(
    (risk, goal),
    {"equity": 40, "debt": 40, "gold": 20}
    )

    if user_alloc:
        if total_user > 100:
            return _set(
            state, start,
            "Your allocation exceeds 100%. Please adjust.",
            "advisor_agent",
            0.9,
            "validation",
            "advisor",
            "invalid_allocation"
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
    # 🔥 ADD THIS BLOCK HERE (REDISTRIBUTION)
    # -------------------------
    
    # -------------------------
    # NORMALIZE AFTER CAPS (FINAL FIX)
    # -------------------------
    total = sum(final_alloc.values())
    adjustable = []
    diff = 0
    if total < 100:

        # -------------------------
        # CASE 1: FULL user allocation
        # -------------------------
        if total_user == 100:

            remaining = 100 - total

            safe_assets = [k for k in default_alloc if k not in MAX_LIMITS]

            if safe_assets:
                share = remaining // len(safe_assets)

                for k in safe_assets:
                    final_alloc[k] = final_alloc.get(k, 0) + share

        # -------------------------
        # CASE 2: PARTIAL user allocation
        # -------------------------
        else:
            diff = 100 - total

            for asset in default_alloc:
                if asset not in final_alloc:
                    final_alloc[asset] = 0

            adjustable = [k for k in default_alloc if k not in MAX_LIMITS]

            if not adjustable:
                adjustable = list(final_alloc.keys())

            share = diff // len(adjustable)

            for k in adjustable:
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

        labels = [
                ("Equity / Dividend funds", "growth + income"),
                ("Debt / Hybrid funds", "stability + income"),
            ("Gold / Liquid", "diversification")
            ]
        
        amount_block += "\n📊 Suggested split:\n\n"
       
        for asset, percent in final_alloc.items():
            fund_amount = int(amount * percent / 100)
    
            amount_block += f"- ₹{fund_amount:,} ({percent}%) → {asset.capitalize()}\n"
    
    if investment == "sip":
        sip_amount = f"₹{amount:,}/month" if amount else "₹5,000/month"
    elif investment == "lump sum":
        sip_amount = f"₹{amount:,} (one-time)" if amount else "₹50,000 (one-time)"
    else:
        sip_amount = "your investment amount"


    # -------------------------
    # ENDING LINE
    # -------------------------
    ending_line = ""

    if is_execution:
        ending_line = ""

    elif is_suggestion:
        ending_line = "If you want, I can help you set this up step-by-step."

    else:
        ending_line = "If you want, I can suggest specific funds or help you set this up step-by-step."
    
    FUND_SUGGESTIONS = {

    # ---------------- LOW RISK ----------------
    ("low", "income", "sip"): [
        "HDFC Corporate Bond Fund (SIP)",
        "ICICI Prudential Equity Savings Fund (SIP)",
        "SBI Conservative Hybrid Fund (SIP)"
    ],

    ("low", "income", "lump sum"): [
        "HDFC Short Term Debt Fund",
        "ICICI Corporate Bond Fund",
        "Axis Banking & PSU Debt Fund"
    ],

    ("low", "growth", "sip"): [
        "HDFC Balanced Advantage Fund",
        "ICICI Balanced Advantage Fund",
        "SBI Equity Hybrid Fund"
    ],

    ("low", "growth", "lump sum"): [
        "ICICI Balanced Advantage Fund",
        "HDFC Hybrid Equity Fund",
        "SBI Balanced Advantage Fund"
    ],

    # ---------------- MEDIUM RISK ----------------
    ("medium", "income", "sip"): [
        "ICICI Regular Savings Fund",
        "HDFC Hybrid Debt Fund",
        "SBI Equity Savings Fund"
    ],

    ("medium", "income", "lump sum"): [
        "ICICI Equity Savings Fund",
        "HDFC Balanced Advantage Fund",
        "UTI Regular Savings Fund"
    ],

    ("medium", "growth", "sip"): [
        "Parag Parikh Flexi Cap Fund",
        "ICICI Bluechip Fund",
        "Mirae Asset Large Cap Fund"
    ],

    ("medium", "growth", "lump sum"): [
        "UTI Flexi Cap Fund",
        "Kotak Flexi Cap Fund",
        "Axis Growth Opportunities Fund"
    ],

    # ---------------- HIGH RISK ----------------
    ("high", "income", "sip"): [
        "HDFC Dividend Yield Fund",
        "ICICI Equity & Debt Fund",
        "UTI Equity Income Fund"
    ],

    ("high", "income", "lump sum"): [
        "ICICI Dividend Yield Fund",
        "HDFC Equity Savings Fund",
        "SBI Equity Income Fund"
    ],

    ("high", "growth", "sip"): [
        "SBI Small Cap Fund",
        "Nippon India Small Cap Fund",
        "Axis Growth Opportunities Fund"
    ],

    ("high", "growth", "lump sum"): [
        "Quant Small Cap Fund",
        "Nippon Small Cap Fund",
        "SBI Focused Equity Fund"
    ],
    }


    if is_suggestion:

        # ✅ default fallback
        selected_funds = [
        "HDFC Balanced Advantage Fund",
        "ICICI Prudential Equity Savings Fund",
        "SBI Flexi Cap Fund"
        ]

        if risk and goal and investment:
            key = (risk, goal, investment)

            if key in FUND_SUGGESTIONS:
                selected_funds = FUND_SUGGESTIONS[key]
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

        if amount and investment == "sip":

            fv_10 = calculate_sip_future_value(amount, rate, 10)
            fv_15 = calculate_sip_future_value(amount, rate, 15)

            projection_block = "\n\n📈 Future Value Projection:\n\n"
            projection_block += f"- ₹{amount:,}/month → ₹{fv_10:,} in 10 years (10% return)\n"
            projection_block += f"- ₹{amount:,}/month → ₹{fv_15:,} in 15 years (10% return)\n"
        
        elif investment == "lump sum":

            fv_10 = calculate_lumpsum_future_value(amount, rate, 10)
            fv_15 = calculate_lumpsum_future_value(amount, rate, 15)

            projection_block += f"- ₹{amount:,} → ₹{fv_10:,} in 10 years (10% return)\n"
            projection_block += f"- ₹{amount:,} → ₹{fv_15:,} in 15 years (10% return)\n"

        # ✅ ONLY read from state
        selected_funds = state.get("selected_funds", [])

        if not selected_funds:
            selected_funds = [
            "HDFC Balanced Advantage Fund",
            "ICICI Prudential Equity Savings Fund",
            "SBI Flexi Cap Fund"
            ]

        fund_split = []

        if selected_funds and amount:

            alloc_values = list(final_alloc.values())

            for i, fund in enumerate(selected_funds[:len(alloc_values)]):
                percent = alloc_values[i]
                fund_amount = int(amount * percent / 100)

                fund_split.append(f"₹{fund_amount} → {fund}")

        execution_block = "\n\n🚀 Your execution plan:\n\n"
        execution_block += f"💰 Investment: {sip_amount}\n\n"

        if fund_split:
            execution_block += "📊 Allocation split:\n"
            execution_block += "\n".join(fund_split) + "\n\n"

        execution_block += alloc([
                "1. Start investment via your broker/app (Groww, Zerodha, etc.)",
                "2. Enable auto-debit for SIP consistency",
                "3. Do not stop during market dips",
                "4. Review portfolio every 6–12 months"
                ])

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

        needs_market = any(w in query for w in ["price", "market"])
        needs_news = intent in ["news_invest", "general_news"]
        # -------------------------
        # LLM-BASED NEWS INVEST FLOW (NEW)
        # -------------------------
        if intent == "news_invest":

            news_context = state.get("news_context")

            # fallback → fetch news if missing
            if not news_context:
                news_state = news_agent(state.copy())
                news_context = news_state.get("answer", "")
                state["news_context"] = news_context

            llm = get_llm(temperature=0.3, max_tokens=400)

            prompt = f"""
You are a financial advisor.

User profile:
- Risk: {profile.get("risk")}
- Goal: {profile.get("goal")}
- Investment: {profile.get("investment_type")}

Market news:
{news_context[:1000]}

Task:
- Suggest 2–3 stocks or sectors
- Align with user risk profile
- Avoid risky suggestions for low-risk users
- Be concise

Output:
- Short insight
- Recommendations
- Reasoning
"""

        try:
            response = llm.invoke(prompt)
            answer = (response.content or "").strip()

            if not answer:
                answer = "Unable to generate recommendation based on news."

        except Exception:
            answer = "Error generating recommendation."

        return _set(
        state, start,
        answer,
        "advisor_agent",
        0.9,
        "llm_reasoning",
        "advisor",
        "news_invest"
        )

    # -------------------------
    # TOOL ORCHESTRATION (FIXED)
    # -------------------------
    context = {}
    tools = state.setdefault("tools_used", [])

    try:
        # ✅ Advisor starts FIRST (correct order)
        state.setdefault("trace", []).append({
        "agent": "advisor_agent",
        "action": "orchestration"
        })
        
        
        available_fields = sum([
            bool(profile.get("risk")),
            bool(profile.get("goal")),
            bool(profile.get("investment_type"))
        ])
    
        # ✅ Call risk agent ONLY if user didn't already specify risk
        if available_fields > 0 and not profile.get("risk"):
            risk_state = risk_agent(state.copy())

            # ✅ ALWAYS trace
            state.setdefault("trace", []).append({
                "agent": "risk_agent",
                "action": "evaluation"
            })

            context["risk"] = risk_state.get("answer", "")

            # ✅ tools separate
            if "risk_agent" not in tools:
                tools.append("risk_agent")

        # Optional
        if needs_market:
            market_state = market_agent(state.copy())
            context["market"] = market_state.get("answer", "")
            state["market_context"] = market_state.get("answer", "")
            if "market_agent" not in tools:
                tools.append("market_agent")

        if needs_news:
            news_state = news_agent(state.copy())
            context["news"] = news_state.get("answer", "")
            state["news_context"] = news_state.get("answer", "")
            if "news_agent" not in tools:
                tools.append("news_agent")
        
        RISK_KEYWORDS = {
        "low": ["low risk", "safe", "secure", "no loss"],
        "medium": ["balanced", "moderate", "some risk"],
        "high": ["high risk", "aggressive", "maximize return", "fast growth"]
        }

        RETURN_KEYWORDS = {
        "low": ["low return", "stable income", "fixed income"],
        "medium": ["decent return", "steady growth"],
        "high": ["high return", "maximum return", "high growth"]
        }

        GOAL_KEYWORDS = {
        "growth": ["growth", "aggressive growth", "long term growth"],
        "income": ["income", "cash flow", "regular income"]
        }
        
        def detect_level(query, mapping):
            detected = []
            for level, keywords in mapping.items():
                if any(k in query for k in keywords):
                    detected.append(level)
            return detected

        risk_signals = detect_level(query, RISK_KEYWORDS)
        return_signals = detect_level(query, RETURN_KEYWORDS)
        goal_signals = detect_level(query, GOAL_KEYWORDS)

        conflicts = []

        # Risk vs Return
        if "low" in risk_signals and "high" in return_signals:
            conflicts.append("low risk vs high return")

        if "high" in risk_signals and "low" in return_signals:
            conflicts.append("high risk vs low return")

        # Risk vs Goal
        if "low" in risk_signals and "growth" in goal_signals:
            conflicts.append("low risk vs aggressive growth")

        if "high" in risk_signals and "income" in goal_signals:
            conflicts.append("high risk vs stable income")

        # Return vs Goal
        if "low" in return_signals and "growth" in goal_signals:
            conflicts.append("low return vs growth expectation")

        if "high" in return_signals and "income" in goal_signals:
            conflicts.append("high return vs stable income focus")

        # priority: growth > return wording > risk wording
        if "growth" in goal_signals:
            profile["goal"] = "growth"

        if "high" in risk_signals:
            profile["risk"] = "high"


        conflict_flag = False
        conflict_msgs = []



        # LOW risk conflicts
        if risk == "low" and any(w in query for w in [
        "aggressive", "high return", "maximum return", "fast growth"
        ]):
            conflict_msgs.append("low risk vs high return/aggressive growth")

        # HIGH risk contradictions
        if risk == "high" and any(w in query for w in [
        "low return", "stable return", "guaranteed"
        ]):
            conflict_msgs.append("high risk vs low/stable return")

        # GROWTH contradictions
        if goal == "growth" and any(w in query for w in [
        "low return", "safe return"
        ]):
            conflict_msgs.append("growth vs low return")

        # INCOME contradictions
        if goal == "income" and any(w in query for w in [
        "high return", "aggressive"
        ]):
            conflict_msgs.append("income vs aggressive growth")

        # FINAL FLAG
        if conflict_msgs:
            conflict_flag = True
            conflict_msg = (
            "Your preferences include some conflicting goals: "
            + ", ".join(conflict_msgs)
            + ". Typically, higher returns require taking higher risk."
            )


        # THEN: advisor calls rag
        if is_decision and available_fields < 2:

            rag_state = rag_agent(state.copy())

            state.setdefault("trace", []).append({
                "agent": "rag_agent",
                "action": "retrieval"
            })

            ans = rag_state.get("answer") or ""

            if ans and not any(x in ans.lower() for x in [
                "unable",
                "couldn't find",
                "no information"
                ]):
                context["knowledge"] = ans

        insights = []

        if context.get("knowledge"):
            clean_knowledge = context["knowledge"].replace("📚 Based on internal documents.", "")
            insights.append(clean_knowledge.strip())

        if context.get("risk"):
            insights.append(context["risk"])

        if conflict_flag:
            insights.append(conflict_msg)

        if not insights:
            if risk == "low" and goal == "income":
                insights.append(
               "A conservative strategy focused on stable, income-generating investments is ideal. Your priority should be preserving capital while generating steady returns."
                )

            elif risk == "low" and goal == "growth":
                insights.append(
                "You prefer low risk but still want growth, so a balanced approach with limited equity exposure is suitable."
                )

            elif risk == "medium" and goal == "growth":
                insights.append(
                "A balanced strategy with both equity and debt can help you achieve growth while managing risk."
                )

            elif risk == "medium" and goal == "income":
                    insights.append(
                    "A balanced approach focusing slightly more on stable income assets is suitable."
                )

            elif risk == "high" and goal == "growth":
                insights.append(
                "You can focus on high equity exposure for long-term growth, accepting higher volatility."
                )

            elif risk == "high" and goal == "income":
                insights.append(
                "Even with a higher risk appetite, you should maintain some stable assets for income."
                )

            elif risk:
                insights.append(
                "Your investment strategy should align with your risk tolerance."
                )

            elif goal:
                insights.append(
                "Your investments should be aligned with your financial goals."
                )

            else:
                insights.append(
                "A diversified approach across asset classes is a good starting point."
                )
        insights_text = "\n\n".join(insights)
        
        advice_lines = []
        
        if profile.get("risk") == "low":
            advice_lines.append("Focus more on stable options like debt and hybrid funds")

        elif profile.get("risk") == "medium":
            advice_lines.append("Balance between equity and debt for growth and stability")

        elif profile.get("risk") == "high":
            advice_lines.append("You can take higher exposure to equity for long-term growth")

        if profile.get("goal") == "growth":
            advice_lines.append("Include equity exposure to maximize long-term returns")

        elif profile.get("goal") == "income":
            advice_lines.append("Prioritize stable and income-generating investments")

        if profile.get("investment_type") == "sip":
            advice_lines.append("Continue SIP for disciplined investing over time")

        if risk == "high" and goal == "income":
            insights.append(
            "Focus on dividend-paying equities and income-generating assets while maintaining some stability."
            )
        
        allocation_hint = ""

        # -------------------------
        # FULL CASE (risk + goal)
        # -------------------------
        labels = ["Equity", "Debt", "Gold"]

        
        allocation_hint = "\n".join([
            f"- {v}% {k.capitalize()}"
            for k, v in final_alloc.items()
            ])

        if advice_lines:
                advice_text = "\n".join(f"- {line}" for line in advice_lines)
        else:
                advice_text = "- Maintain diversification across asset classes"
        warning_msg = warning_msg.strip() 
        if is_execution:

            answer = (
            f"Great — here’s how you can invest {sip_amount}:\n\n"
            f"{amount_block}\n"
            f"{suggestion_block if suggestion_block else ''}\n"
            f"{projection_block if projection_block else ''}\n"
            f"{execution_block if execution_block else ''}"
            )

        else:

            answer = (
            f"{warning_msg}\n"
            f"{allocation_gap_msg}\n\n"
            "Got it — based on what you've shared:\n\n"
            f"{profile_section}"
            "---\n\n"
            "Here’s what this means for you:\n\n"
            f"{insights_text}\n\n"
            "---\n\n"
            "📌 Recommended approach:\n\n"
            f"{advice_text}\n\n"
            "---\n\n"
            "💡 Suggested allocation:\n\n"
            f"{allocation_hint}\n\n"
            f"{amount_block if amount_block else ''}"
            f"{suggestion_block if suggestion_block else ''}\n\n"
            "---\n\n"
            f"{ending_line}"
        )
        
        profile = {k: v for k, v in profile.items() if v}
        
        state["profile"] = profile
        
        state.setdefault("memory", []).append({
            "query": state.get("query"),
            "assistant": answer,
            "stage": state.get("stage"),
            "agent": "advisor_agent",
            "profile": state.get("profile")
            })
        
        return _set(
            state, start,
            answer,
            "advisor_agent",
            0.85,
            "advisor_reasoning",
            "advisor",
            "orchestration",
            extra={
                "tools": tools,
                "advisor_insights": insights_text,
                "advisor_allocation": final_alloc,
                "advisor_advice": advice_text
                },
            add_trace=False 
            )

    except Exception as e:
        print(f"[ADVISOR ERROR] {e}")

        return _set(
            state, start,
            "Unable to process request.",
            "advisor_agent", 0.2, "error", "advisor",
            "error",
            {"error": str(e)}
        )