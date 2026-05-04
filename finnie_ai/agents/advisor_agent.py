from utils.state import AgentState
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent
import re
import time
import random
from utils.llm import get_llm
from utils.finance_constants import (ALLOCATION_MAP,MAX_LIMITS,
FUND_SUGGESTIONS)
from utils.fund_utils import extract_user_allocation,merge_allocation
from utils.format_utils import alloc
from utils.calculation_utils import calculate_lumpsum_future_value,calculate_sip_future_value
from utils.state_utils import set_state
from utils.parsing_utils import normalize_term
# Load environment variables (API keys etc.)
from dotenv import load_dotenv
import hashlib
load_dotenv()



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

    last_msg = memory[-1] if memory else {}
    last_assistant = last_msg.get("assistant") or ""
    last_stage = last_msg.get("stage") or state.get("stage")

    prompt = f"""You are classifying user intent in a financial assistant.

Previous stage: {last_stage}

Last assistant message:
{last_assistant[:300]}

User message:
{query}

Classify into ONE of:

1. confirm → user agrees or wants to proceed (yes, ok, please, go ahead)
2. projection → user asks about returns, future value, growth
3. execution → user wants to start/invest/do it now
4. suggestion → user asks for funds/recommendations/options
5. modify → user changes inputs (risk, goal, amount, allocation)
6. advice → general question or unclear intent
7. news_invest → user wants investment ideas based on news
8. general_news → user wants latest news

Rules:
- Short replies after suggestion → confirm
- Asking "what returns?" → projection
- Saying "start", "invest", "do it" → execution
- Asking "which funds?" → suggestion
- Changing numbers/profile → modify
- If unclear → advice

Answer ONLY one word."""

    try:
        res = llm.invoke(prompt)
        return res.content.strip().lower()
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
    #DETECTING INTENT OF USER QUERY 
    llm_intent = detect_intent_llm(query, state, llm)
    print("LLM Intent: ",llm_intent)    
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

    # -------------------------
    # DETECT PROFILE COMPLETION MOMENT
    # -------------------------
    just_completed_profile = False

    if profile_complete and last_stage is None:
        just_completed_profile = True

    elif profile_complete and last_stage == "advice":
            # if amount was missing before and now provided
        if amount_match:
            just_completed_profile = True

    # -------------------------
    # HYBRID STAGE CONTROL
    # -------------------------

    if len(query.split()) <= 2 and llm_intent in ["confirm", "suggestion"]:
        intent = "confirm"
    else:
        intent = llm_intent


    state["intent"] = intent

    if last_stage is None:
        stage = "advice"

    elif last_stage == "advice":
        if intent in ["confirm", "suggestion"]:
            stage = "suggestion"
        elif intent == "modify":
            stage = "advice"
        else:
            stage = "advice"

    elif last_stage == "suggestion":
        if intent in ["confirm", "execution"]:
            stage = "execution"
        elif intent == "projection":
            stage = "projection"
        elif intent == "modify":
            stage = "advice"
        else:
            stage = "suggestion"

    elif last_stage == "projection":
        if intent in ["confirm", "execution"]:
            stage = "execution"
        elif intent == "modify":
            stage = "advice"
        else:
            stage = "projection"

    else:
        stage = "advice" 

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

        answer = f"""
Got it — I can help with that.

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

    answer = ""
    if user_alloc and not any([risk, goal, investment]):
        answer += "\n\n💡 Tip: Share your risk level or goal for more personalized advice."

    # -------------------------
    # NO INFO → ask everything
    # -------------------------
    if user_alloc and not any([profile.get("risk"), profile.get("goal"), profile.get("investment_type")]):
            pass

   
    # -------------------------
    # GUARDRAILS (VERY IMPORTANT)
    # -------------------------

    # Prevent skipping advice → suggestion directly
    if stage == "suggestion" and last_stage not in [None, "advice"]:
        stage = "advice"
    
    # Prevent jumping to execution early
    if stage == "suggestion" and last_stage not in [None, "advice"] and intent != "suggestion":
        stage = "advice"

    # Prevent regression
    if last_stage == "suggestion" and stage == "advice" and intent == "projection":
        stage = "projection"
       
    
    state["stage"] = stage

    # derive flags (single source of truth)
    is_suggestion = stage == "suggestion"
    is_projection = stage == "projection"
    is_execution = stage == "execution"


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
        needs_news = (
            intent in ["news_invest", "general_news"]
            and any(word in query for word in ["news", "market", "impact", "recent"])
            )
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

            prompt = f"""You are a financial advisor.

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
- Reasoning"""

            try:
                response = llm.invoke(prompt)
                answer = (response.content or "").strip()

                if not answer:
                    answer = "Unable to generate recommendation based on news."

            except Exception:
                answer = "Error generating recommendation."

            return set_state(
                state,
                start,
                answer=answer,
                agent="advisor_agent",
                confidence=0.9,
                decision_source="llm_reasoning",
                answer_source="advisor",
                trace_action="news_invest"
                )

    # -------------------------
    # TOOL ORCHESTRATION (FIXED)
    # -------------------------
    context = {}
    tools = state.setdefault("tools_used", [])

    try:

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
        
    

        conflict_msgs = []
        conflict_flag = False

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
        
        allocation_hint = "\n".join([
            f"- {v}% {k.capitalize()}"
            for k, v in final_alloc.items()
            ])

        if advice_lines:
                advice_text = "\n".join(f"- {line}" for line in advice_lines)
        else:
                advice_text = "- Maintain diversification across asset classes"
        
        warning_msg = warning_msg.strip() 

        # -------------------------
# STAGE-BASED RESPONSE (FIX)
# -------------------------
        fv_10 = None
        fv_15 = None

        if amount:  
            rate = {"low": 8, "medium": 10, "high": 12}.get(risk, 10)
            if investment == "sip":
                fv_10 = calculate_sip_future_value(amount, rate, 10)
                fv_15 = calculate_sip_future_value(amount, rate, 15)

            elif investment == "lump sum":
                fv_10 = calculate_lumpsum_future_value(amount, rate, 10)
                fv_15 = calculate_lumpsum_future_value(amount, rate, 15)
        if is_execution:   
            answer = (
            f"Great — here’s how you can invest {sip_amount}:\n\n"
            f"{amount_block}\n"
            f"{projection_block}\n"
            f"{execution_block}"
            )

        elif is_projection:

            if investment == "sip":
                line1 = f"- ₹{amount:,}/month → ₹{fv_10:,} in 10 years ({rate}% return)"
                line2 = f"- ₹{amount:,}/month → ₹{fv_15:,} in 15 years ({rate}% return)"
            else:
                line1 = f"- ₹{amount:,} → ₹{fv_10:,} in 10 years ({rate}% return)"
                line2 = f"- ₹{amount:,} → ₹{fv_15:,} in 15 years ({rate}% return)"

            answer = (
                "📈 Future Value Projection:\n\n"
                f"{line1}\n"
                f"{line2}\n"
                "👉 Say 'go ahead' to see how to invest step-by-step."
                )

        elif is_suggestion:
            answer = (
            f"📊 Suggested funds:\n\n"
            f"{alloc(state.get('selected_funds', []))}\n\n"
            "If you want, I can help you set this up step-by-step."
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
            f"{amount_block if amount_block else ''}\n\n"
            "💡 If you want, I can suggest specific funds."
        )
        
        profile = {k: v for k, v in profile.items() if v}
        
        state["profile"] = profile
        
        print("profile ", profile)
        
        return set_state(
            state,
            start,
            answer=answer,
            agent="advisor_agent",
            confidence=0.85,
            decision_source="advisor_reasoning",
            answer_source="advisor",
            trace_action="orchestration",
            extra={
                "tools_used": tools,
                "advisor_insights": insights_text,
                "advisor_allocation": final_alloc,
                "advisor_advice": advice_text
            },
            add_trace=False
            )           

    except Exception as e:
        print(f"[ADVISOR ERROR] {e}")

        return set_state(
            state,
            start,
            answer="Unable to process request.",
            agent="advisor_agent",
            confidence=0.2,
            decision_source="error",
            answer_source="advisor",
            trace_action="error",
            extra={ 
                "error": str(e),
                "error_type": type(e).__name__,
                "error_stage": state.get("stage")
                }
            )