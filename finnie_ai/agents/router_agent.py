from utils.state import AgentState
from utils.llm import get_llm
import re
from utils.prompts import ROUTER_PROMPT
from dotenv import load_dotenv
from difflib import get_close_matches
load_dotenv()

ASSET_MAP = {
    "equity": ["equity", "stocks", "shares"],
    "debt": ["debt", "bonds", "fixed income"],
    "gold": ["gold"],
    "crypto": ["crypto", "bitcoin", "ethereum"],
    "real_estate": ["real estate", "property"],
}

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}

FINANCE_KEYWORDS = [
    "invest", "investment", "sip", "lump", "equity",
    "debt", "gold", "crypto", "fund", "portfolio",
    "stock", "returns", "bonds"
]

def is_finance_related(query: str) -> bool:
    words = query.lower().split()

    for word in words:
        match = get_close_matches(word, FINANCE_KEYWORDS, n=1, cutoff=0.75)
        if match:
            return True

    return False

# -------------------------
# CENTRAL SETTER
# -------------------------
def _set(state, category, confidence, source, reason=None):
    state["category"] = category
    state["confidence"] = confidence
    state["decision_source"] = source

    state.setdefault("trace", []).append({
        "agent": "router_agent_v3",
        "action": "classify",
        "category": category,
        "method": source,
        "reason": reason
    })

    return state


# -------------------------
# CLEAN QUERY
# -------------------------
def clean_query(query: str):
    return re.sub(r"[^\w\s]", "", query.lower().strip())


# -------------------------
# BUILD FULL PROMPT (MAIN + ROUTER)
# -------------------------
def build_full_prompt(state):
    query = state.get("query", "")
    stage = state.get("stage", "")
    profile = state.get("profile", {})
    memory = state.get("memory", [])

    #context = "\n".join([str(m) for m in memory[-3:]])
    context = "\n".join([
    f"User: {m.get('query')} | Category: {m.get('category')}"
    for m in memory[-3:]
    ])

    MAIN_PROMPT = """You are a financial assistant system.

You have access to:
- User profile
- Conversation stage
- Past conversation

Use this information to understand user intent.
"""

    return f"""
{MAIN_PROMPT}

-------------------------
USER CONTEXT
-------------------------
Stage: {stage}
Profile: {profile}
History:
{context}

-------------------------
TASK
-------------------------
{ROUTER_PROMPT.format(query=query)}
"""


# -------------------------
# AGENT 1: PRIMARY CLASSIFIER
# -------------------------
def classify_agent(state):
    llm = get_llm(model="gpt-4o", temperature=0)

    prompt = build_full_prompt(state)
    res = llm.invoke(prompt)

    # Clean output (very important)
    category = res.content.strip().lower()
    category = category.split()[0]

    if category in VALID_CATEGORIES:
        return {
            "category": category,
            "confidence": 0.8,
            "reason": "primary_classification"
        }

    return None


# -------------------------
# AGENT 2: VALIDATOR (SELF-CHECK)
# -------------------------
def validator_agent(state, first_result):
    llm = get_llm(model="gpt-4o-mini", temperature=0.3)

    query = state.get("query", "").strip().lower()
    stage = state.get("stage", "")
    profile = state.get("profile", {})
    memory = state.get("memory", [])

    context = "\n".join([str(m) for m in memory[-3:]])


    prompt = f"""You are a strict financial intent validator.

Your job is to VERIFY and CORRECT the classification.

Be critical. Do NOT agree blindly.

-------------------------
CONTEXT
-------------------------
Stage: {stage}
Profile: {profile}
Recent History:
{context}

-------------------------
QUERY
-------------------------
{query}

Initial classification: {first_result["category"]}

-------------------------
INTENT RULES
-------------------------
advisor → user wants decision or recommendation  
rag → user wants explanation or learning  
risk → user evaluates safety only (not asking what to do)  
market → price queries  
news → updates  
none → non-finance  

-------------------------
PRIORITY (IMPORTANT)
-------------------------
1. none  
2. advisor  
3. rag  
4. risk  
5. market  
6. news  

-------------------------
KEY LOGIC
-------------------------
- "safe option" → advisor (NOT risk)
- "risk explained" → rag (NOT risk)
- "risk" alone → rag
- "is it safe" → risk

IMPORTANT:
Use context when needed.
Do NOT rely only on keywords.

-------------------------
TASK
-------------------------

If initial classification is WRONG → correct it  
If it is correct → keep it  

Return ONLY one word:
market / risk / advisor / news / rag / none"""

    res = llm.invoke(prompt)

    category = res.content.strip().lower()
    category = category.replace(".", "").replace(",", "")
    category = category.split()[0]

    if category in VALID_CATEGORIES:
        return {
            "category": category,
            "confidence": 0.7,
            "reason": "validated"
        }

    return None

# -------------------------
# ROUTER AGENT V3 (PURE AGENTIC)
# -------------------------
def router_agent(state: AgentState) -> AgentState:
    query = state.get("query", "")

    expected = state.get("expected_next_input")

    if expected:
        return _set(
        state,
        "advisor",
        0.99,
        "expected_input",
        expected
        )
    
    # -------------------------
    # MEMORY STAGE SYNC
    # -------------------------
    memory = state.get("memory", [])
    if memory:
        last_stage = memory[-1].get("stage")
        if last_stage:
            state["stage"] = last_stage

    if memory and len(memory) >= 1:
        last_stage = memory[-1].get("stage")

        if last_stage == "ask_investment_type":
            state["stage"] = "advisor"
            return _set(state, "advisor", 0.95, "followup", "investment_type_response")
    
    if memory:
        last_agent = memory[-1].get("agent")

        if last_agent == "advisor_agent":
            if any(word in query for word in ["sip", "lump", "lumpsum"]):
                return _set(state, "advisor", 0.95, "followup", "investment_type_response")
    

    vague_patterns = ["is it good", "should i", "worth it"]
    query_clean = re.sub(r"[^\w\s]", "", query.lower()).strip()

    if any(p in query_clean for p in vague_patterns):
        return _set(state, "advisor", 0.95, "vague_guardrail")
    
    amount_patterns = [
        r"\b\d{3,7}\b",
        r"amount\s*\d+",
        r"invest\s*\d+",
        r"\d+\s*rs",
        r"₹\s*\d+"
        ]

    if any(re.search(p, query) for p in amount_patterns):
        if memory and memory[-1].get("agent") == "advisor_agent":
            return _set(state, "advisor", 0.96, "followup", "amount_detected")

    # -------------------------
    # ALLOCATION DETECTION (FIXED)
    # -------------------------

    pattern1 = r"\d+%\s*([a-zA-Z ]+)"        # 100% crypto
    pattern2 = r"([a-zA-Z ]+)\s*\d+%"        # crypto 100%

    match1 = re.search(pattern1, query.lower())
    match2 = re.search(pattern2, query.lower())

    match = match1 or match2
    if match:
        asset_raw = match.group(1).strip().lower()

        valid_assets = [a for aliases in ASSET_MAP.values() for a in aliases]
        match_asset = get_close_matches(asset_raw, valid_assets, n=1, cutoff=0.7)

        if match_asset or is_finance_related(query):
            return _set(state, "advisor", 0.95, "rule", "allocation_detected")

    # -------------------------
    # STEP 1: PRIMARY CLASSIFICATION
    # -------------------------

    first = classify_agent(state)

    if not first:
        return _set(state, "advisor", 0.5, "fallback", "invalid_llm_output")

    # -------------------------
    # STEP 2: VALIDATION
    # -------------------------
    second = validator_agent(state, first)

    if second:
    # Only override if DIFFERENT and HIGH CONFIDENCE
        if second["category"] != first["category"]:
            if second["confidence"] >= 0.9:
                return _set(
                state,
                second["category"],
                second["confidence"],
                "agent_corrected",
                second["reason"]
                )

    # -------------------------
    # STEP 3: FALLBACK TO FIRST
    # -------------------------
    return _set(
        state,
        first["category"],
        first["confidence"],
        "agent",
        first["reason"]
    )
    