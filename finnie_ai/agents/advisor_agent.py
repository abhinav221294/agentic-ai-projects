from utils.state import AgentState
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent
import re
import time

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


# Allocation mapping
ALLOCATION_MAP = {

    # LOW RISK
    ("low", "income"): (30, 50, 20),
    ("low", "growth"): (40, 40, 20),

    # MEDIUM
    ("medium", "income"): (40, 40, 20),
    ("medium", "growth"): (60, 25, 15),

    # HIGH RISK
    ("high", "income"): (70, 20, 10),
    ("high", "growth"): (80, 15, 5),
}



def advisor_agent(state: AgentState) -> AgentState:
    start = time.time()

    profile = (state.get("profile") or {}).copy()
    memory = state.get("memory", [])
    #last_msg = memory[-1] if memory else {}
    #raw_query = last_msg.get("user", state.get("query", "")).strip()
    raw_query = state.get("query", "").strip()
    query = re.sub(r"[^\w\s]", " ", raw_query).lower().strip()
    amount_match = re.search(r"\b\d{4,7}\b", query)

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


    # Start with existing profile (if any)
    # -------------------------
    # EXTRACT RISK
    # -------------------------
    if "low" in query:
        profile["risk"] = "low"
    elif "medium" in query:
        profile["risk"] = "medium"
    elif "high" in query:
        profile["risk"] = "high"

    # -------------------------
    # EXTRACT GOAL
    # -------------------------
    if "income" in query:
        profile["goal"] = "income"
    elif "growth" in query:
        profile["goal"] = "growth"

    # -------------------------
    # EXTRACT INVESTMENT TYPE
    # -------------------------
    if "sip" in query:
        profile["investment_type"] = "sip"
    elif "lump sum" in query:
        profile["investment_type"] = "lump sum"

    #    🔥 SAVE BACK
    #state["profile"] = profile

    #print("Initial profile: ", profile)


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
    elif "lump sum" in query:
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

    # -------------------------
    # NO INFO → ask everything
    # -------------------------
    if missing:
        followup = "\n\nTo refine this further, you can also share:\n"
        followup += "\n".join([f"- {m}" for m in missing])

        answer = f"""
Got it — I can help with that.

{followup}

Can you share that?
"""
        state["profile"] = profile
        state["stage"] = "collect_profile"

        return _set(
        state, start,
        answer,
        "advisor_agent",
        0.9,
        "clarification",
        "advisor",
        "ask_missing"
    )

    
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

    if last_stage == "suggestion" and not is_decision and not is_profile_update:
        is_execution = True

    
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
        
        alloc_values = ALLOCATION_MAP.get((risk, goal), (40, 40, 20))
        amount_block += "\n📊 Suggested split:\n\n"
       
        for i, percent in enumerate(alloc_values):
            fund_amount = int(amount * percent / 100)
            name, desc = labels[i]

            amount_block += f"- ₹{fund_amount:,} ({percent}%) → {name} ({desc})\n"

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
        state["stage"] = "suggestion"

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
        
        alloc_values = ALLOCATION_MAP.get((risk, goal), (40, 40, 20))

        execution_block = ""

        labels = ["Equity", "Debt", "Gold"]

        allocation_hint = "\n".join([
        f"- {alloc_values[i]}% {labels[i]}"
        for i in range(3)
        ])

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

            for i, fund in enumerate(selected_funds[:3]):
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
    needs_news = any(w in query for w in ["news", "latest"])


    

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
            if "market_agent" not in tools:
                tools.append("market_agent")

        if needs_news:
            news_state = news_agent(state.copy())
            context["news"] = news_state.get("answer", "")
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

        alloc_values = ALLOCATION_MAP.get((risk, goal), (40, 40, 20))

        allocation_hint = "\n".join([
        f"- {alloc_values[i]}% {labels[i]}"
            for i in range(3)
        ])

        if advice_lines:
                advice_text = "\n".join(f"- {line}" for line in advice_lines)
        else:
                advice_text = "- Maintain diversification across asset classes"

        answer = ("Got it — based on what you've shared:\n\n"
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
    f"{suggestion_block if suggestion_block else ''}"
    f"{execution_block if execution_block else ''}\n\n"
    f"{projection_block if projection_block else ''}\n\n"
    "---\n\n"
    f"{ending_line}"
    )
        
        profile = {k: v for k, v in profile.items() if v}
        
        if is_execution:
            state["stage"] = "execution"
        elif is_suggestion:
            state["stage"] = "suggestion"
        else:
            state["stage"] = "advice"
        
        state["profile"] = profile 
        return _set(
        state, start,
        answer,
        "advisor_agent",
        0.85,
        "advisor_reasoning",
        "advisor",
        "orchestration",
        {"tools": tools},
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