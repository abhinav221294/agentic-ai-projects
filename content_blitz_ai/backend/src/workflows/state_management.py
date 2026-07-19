import time

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):

    # =========================
    # USER INPUT
    # =========================
    user_id: str
    conversation_id: str
    user_query: str

    # =========================
    # MESSAGES (LLM CONTEXT)
    # =========================
    messages: List[Dict[str, str]]

    # =========================
    # CONVERSATIONAL MEMORY
    # =========================
    conversation_history: List[Dict[str, str]]

    # =========================
    # SHORT-TERM WORKFLOW MEMORY
    # =========================
    current_intent: Optional[str]

    current_task: Optional[str]

    active_agent: Optional[str]

    workflow_step: Optional[str]

    intermediate_outputs: Dict[str, Any]

    tool_outputs: Dict[str, Any]

    # =========================
    # LONG-TERM MEMORY
    # =========================
    retrieved_memories: List[str]

    user_preferences: Dict[str, Any]

    memory: List[Dict[str, Any]]

    # =========================
    # RESEARCH CONTEXT
    # =========================
    research_data: Optional[str]

    sources: List[str]

    # =========================
    # CONTENT OUTPUTS
    # =========================
    blog_content: Optional[str]

    linkedin_content: Optional[str]

    content_plan: Optional[Dict[str, Any]]

    image_prompt: Optional[str]

    image_url: Optional[str]

    generated_assets: List[Dict[str, Any]]

    # =========================
    # SYSTEM CONTROL
    # =========================
    status: Optional[str]

    retry_count: int

    errors: List[str]

    execution_logs: List[str]

    next_action: Optional[str]

    final_response: Optional[str]

    metadata: Dict[str, Any]

    # =========================
    # ROUTING / TRACE
    # =========================
    trace: List[Dict[str, Any]]

    category: Optional[str]

    confidence: Optional[float]

    decision_source: Optional[str]

    answer_source: Optional[str]

    execution_time: Optional[float]

    # =========================
    # GENERIC OUTPUT
    # =========================
    answer: Optional[str]


def set_state(
    state: AgentState,
    start=None,

    # =========================
    # CORE
    # =========================
    answer=None,
    agent=None,
    confidence=None,
    category=None,
    status=None,

    # =========================
    # META
    # =========================
    decision_source=None,
    answer_source=None,
    source=None,
    trace_action=None,

    # =========================
    # EXTRA
    # =========================
    extra=None,

    # =========================
    # FLAGS
    # =========================
    add_trace=True,
    update_memory=True
):

    # =========================
    # CORE FIELDS
    # =========================
    if answer is not None:
        state["answer"] = answer
        state["final_response"] = answer

    if agent:
        state["active_agent"] = agent

    if confidence is not None:
        state["confidence"] = confidence

    if category:
        state["category"] = category

    if status:
        state["status"] = status

    if decision_source:
        state["decision_source"] = decision_source

    if answer_source:
        state["answer_source"] = answer_source

    if source:
        state["sources"] = source

    if start:
        state["execution_time"] = round(time.time() - start, 2)

    # =========================
    # EXTRA STATE UPDATES
    # =========================
    if extra:
        state.update(extra)

    # =========================
    # TRACE LOGGING
    # =========================
    if add_trace and trace_action:

        state.setdefault("trace", []).append({
            "agent": agent,
            "action": trace_action,
            "timestamp": time.time(),
            **(extra or {})
        })

    # =========================
    # MESSAGE HISTORY
    # =========================
    if answer:

        state.setdefault("messages", []).append({
            "role": "assistant",
            "content": answer
        })

    # =========================
    # CONVERSATION MEMORY
    # =========================
    if answer:

        state.setdefault("conversation_history", []).append({
            "role": "assistant",
            "content": answer
        })

    # =========================
    # SHORT + LONG TERM MEMORY
    # =========================
    if update_memory and answer:

        memory = state.setdefault("memory", [])

        memory.append({
            "query": state.get("user_query"),
            "assistant": answer,
            "workflow_step": state.get("workflow_step"),
            "agent": agent,
            "intent": state.get("current_intent"),
            "task": state.get("current_task"),
            "timestamp": time.time()
        })

        # Keep latest 10 interactions
        if len(memory) > 10:
            state["memory"] = memory[-10:]

    # =========================
    # DEFAULT METADATA
    # =========================
    state.setdefault("metadata", {})

    state.setdefault("tool_outputs", {})

    state.setdefault("generated_assets", [])

    state.setdefault("execution_logs", [])

    state.setdefault("errors", [])

    state.setdefault("retry_count", 0)

    return state