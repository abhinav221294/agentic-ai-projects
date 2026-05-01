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
Stage: {m.get('stage')}
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

IMPORTANT:
- Use context to understand intent
- Short replies may be continuation
- Do NOT rely on keywords only
"""


# -------------------------
# PURE LLM ROUTER
# -------------------------
def router_agent(state: AgentState) -> AgentState:
    llm = get_llm(model="gpt-4o-mini", temperature=0)

    query = state.get("query", "")

    context = build_context(state)

    prompt = f"""
{context}

{ROUTER_PROMPT.format(query=query)}
"""

    res = llm.invoke(prompt)

    # Clean output
    category = res.content.strip().lower()
    category = category.replace(".", "").replace(",", "")
    category = category.split()[0]

    if category not in VALID_CATEGORIES:
        # Even fallback is LLM-driven philosophy → soft default
        category = "advisor"

    return _set(
        state,
        category,
        0.9,
        "pure_llm",
        "context_reasoned"
    )