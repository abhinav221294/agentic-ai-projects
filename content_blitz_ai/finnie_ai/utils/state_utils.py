import time

def set_state(
    state,
    start=None,
    *,
    # -------- core --------
    answer=None,
    agent=None,
    confidence=None,
    category=None,

    # -------- meta --------
    decision_source=None,
    answer_source=None,
    source=None,   # rag compatibility
    trace_action=None,

    # -------- extension --------
    extra=None,

    # -------- flags --------
    add_trace=True,
    update_memory=True
):
    # -------------------------
    # CORE FIELDS
    # -------------------------
    if answer is not None:
        state["answer"] = answer

    if agent:
        state["agent"] = agent

    if confidence is not None:
        state["confidence"] = confidence

    if category:
        state["category"] = category

    if decision_source:
        state["decision_source"] = decision_source

    if answer_source:
        state["answer_source"] = answer_source

    if source:
        state["source"] = source

    if start:
        state["execution_time"] = round(time.time() - start, 2)

    # -------------------------
    # EXTRA (advisor / market / news specific)
    # -------------------------
    if extra:
        state.update(extra)

    # -------------------------
    # TRACE
    # -------------------------
    if add_trace and trace_action:
        state.setdefault("trace", []).append({
            "agent": agent,
            "action": trace_action,
            **(extra or {})
        })

    # -------------------------
    # MEMORY (SMART CARRY FORWARD)
    # -------------------------
    if update_memory and answer:
        memory = state.setdefault("memory", [])

        last_funds = next(
            (m.get("selected_funds") for m in reversed(memory) if m.get("selected_funds")),
            None
        )

        memory.append({
            "query": state.get("query"),
            "assistant": answer,
            "stage": state.get("stage"),
            "agent": agent,
            "profile": state.get("profile"),
            "selected_funds": state.get("selected_funds") or last_funds
        })

        if len(memory) > 10:
            state["memory"] = memory[-10:]

    return state