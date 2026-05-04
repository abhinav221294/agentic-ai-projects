# -------------------------
# IMPORTS
# -------------------------
# Agent state schema (shared across agents)
from utils.state import AgentState

# LLM utility to initialize language model
from utils.llm import get_llm

# Router prompt template (defines classification instructions)
from utils.prompts import ROUTER_PROMPT

# Load environment variables (API keys, configs)
from dotenv import load_dotenv

load_dotenv()

from utils.state_utils import set_state

# Allowed routing categories (strict control over outputs)
VALID_CATEGORIES = {"market", "risk", "advisor", "news", "rag", "none"}


# -------------------------
# BUILD CONTEXT (IMPORTANT)
# -------------------------
def build_context(state):
    """
    Builds contextual prompt for LLM routing.

    Includes:
    - Conversation history
    - User profile
    - Current stage

    This helps LLM maintain continuity and avoid keyword-only routing.
    """

    memory = state.get("memory", [])
    stage = state.get("stage", "")
    profile = state.get("profile", {})

    # Take last 3 interactions for context
    history = "\n".join([
        f"""
User: {m.get('query')}
Assistant: {m.get('assistant')}
"""
        for m in memory[-3:]
    ])

    # Final structured context block
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
- Do NOT rely on keywords only
"""


# -------------------------
# LLM FOLLOW-UP ROUTING (FIX)
# -------------------------
# Initialize LLM for follow-up detection (deterministic)
llm = get_llm(temperature=0)

def is_followup_llm(query, memory):
    """
    Uses LLM to determine whether current query
    is a follow-up to previous conversation.
    """

    # Build short history (last 2 turns)
    history = "\n".join([
        f"User: {m.get('query')}\nAssistant: {m.get('assistant')}"
        for m in memory[-2:]
    ])

    # Prompt for binary classification
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

        # Return True if "yes" detected
        return "yes" in res.content.lower()

    except:
        # Fail-safe: assume not follow-up
        return False


# -------------------------
# PURE LLM ROUTER
# -------------------------
def router_agent(state: AgentState) -> AgentState:
    """
    Main routing agent:
    - Detects follow-ups using LLM
    - Uses contextual prompt for classification
    - Routes query to correct agent category
    """

    # -------------------------
    # FOLLOW-UP DETECTION
    # -------------------------
    memory = state.get("memory", [])

    # Get last agent used (if any)
    last_agent = memory[-1].get("agent") if memory else None

    # Initialize LLM for routing (more powerful model)
    llm = get_llm(model="gpt-4o-mini", temperature=0)

    # Current user query
    query = state.get("query", "")

    # Build contextual prompt
    context = build_context(state)

    
    # -------------------------
    # FOLLOW-UP ROUTING
    # -------------------------
    # If follow-up → route to previous agent
    if is_followup_llm(query, memory) and last_agent:
        return set_state(
        state,
        category=last_agent.replace("_agent", ""),
        confidence=0.95,
        decision_source="llm_followup",
        trace_action="followup",
        extra={
            "reason": "continue_context"
        },
        update_memory=False   # 🚨 IMPORTANT (router should not write memory)
        )   

    # -------------------------
    # NORMAL ROUTING (LLM)
    # -------------------------
    # Combine context + router instructions
    prompt = f"""
    {context}

    {ROUTER_PROMPT.format(query=query)}
    """

    # Call LLM for classification
    res = llm.invoke(prompt)

    # Clean output (take first word only)
    category = res.content.strip().lower().split()[0]

    # -------------------------
    # SAFETY CHECK
    # -------------------------
    # Ensure category is valid, fallback to advisor if not
    if category not in VALID_CATEGORIES:
        category = "advisor"

    return set_state(
    state,
    category=category,
    confidence=0.9,
    decision_source="pure_llm",
    trace_action="classify",
    extra={
        "reason": f"llm_output={res.content.strip()}"
    },
    update_memory=False   # 🚨 IMPORTANT
    )