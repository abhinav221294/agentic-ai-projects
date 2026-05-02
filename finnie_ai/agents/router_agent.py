from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import ROUTER_PROMPT
from dotenv import load_dotenv

load_dotenv()

VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}

# -------------------------
# CENTRAL SETTER
# -------------------------
def _set(state, category, confidence, source, reason=None):
    state["category"] = category
    state["confidence"] = confidence
    state["decision_source"] = source

    state.setdefault("trace", []).append({
        "agent": "router_agent_pure",
        "action": "classify",
        "category": category,
        "method": source,
        "reason": reason
    })

    return state

# -------------------------
# BUILD CONTEXT (IMPORTANT)
# -------------------------
def build_context(state):
    memory = state.get("memory", [])
    stage = state.get("stage", "")
    profile = state.get("profile", {})

    history = "\n".join([
        f"""
User: {m.get('query')}
Assistant: {m.get('assistant')}
"""
        for m in memory[-3:]
    ])

    return f"""
You are a stateful financial router.

Context:
- Current Stage: {stage}
- User Profile: {profile}

Recent Conversation:
{history}

Topic: Continue the same financial topic unless user explicitly changes it.

IMPORTANT:
- Continue the same topic unless user clearly changes it
- If user asks a vague follow-up → infer from previous conversation
- Use previous assistant response to understand intent
- Do NOT rely on keywords only"""

# -------------------------
# LLM FOLLOW-UP ROUTING (FIX)
# -------------------------
from utils.llm import get_llm

llm = get_llm(temperature=0)

def is_followup_llm(query, memory):
    history = "\n".join([
        f"User: {m.get('query')}\nAssistant: {m.get('assistant')}"
        for m in memory[-2:]
    ])

    prompt = f"""
Is the user's latest query a follow-up to the previous conversation?

Conversation:
{history}

New query:
{query}

Answer only YES or NO.
"""

    try:
        res = llm.invoke(prompt)
        return "yes" in res.content.lower()
    except:
        return False

# -------------------------
# PURE LLM ROUTER
# -------------------------
def router_agent(state: AgentState) -> AgentState:
    # -------------------------
    # LLM FOLLOW-UP DETECTION (NO KEYWORDS)
    # -------------------------
    memory = state.get("memory", [])
    last_agent = memory[-1].get("agent") if memory else None

    llm = get_llm(model="gpt-4o-mini", temperature=0)

    query = state.get("query", "")

    context = build_context(state)
    is_followup = is_followup_llm(query, memory)

    # -------------------------
    # FOLLOW-UP ROUTING
    # -------------------------
    if is_followup_llm(query, memory) and last_agent:
        return _set(
        state,
        last_agent.replace("_agent", ""),
        0.95,
        "llm_followup",
        "continue_context"
        )

    prompt = f"""
{context}

{ROUTER_PROMPT.format(query=query)}
"""

    res = llm.invoke(prompt)

    # Clean output
    category = res.content.strip().lower().split()[0]
    # hard safety clamp
    
    if category not in VALID_CATEGORIES:
        category = "advisor"

    return _set(
    state,
    category,
    0.9,
    "pure_llm",
    f"llm_output={res.content.strip()}"
    )