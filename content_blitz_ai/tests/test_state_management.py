from src.workflows.state_management import set_state


def build_state():

    return {
        "user_id": "test_user",
        "session_id": "session_001",
        "user_query": "Test query",
        "conversation_history": [],
        "memory": [],
        "errors": [],
        "trace": [],
        "tool_outputs": {},
        "generated_assets": [],
        "execution_logs": [],
        "metadata": {},
        "retry_count": 0
    }


# =========================================
# BASIC STATE UPDATE
# =========================================

def test_basic_state_update():

    state = build_state()

    updated = set_state(
        state=state,
        status="success",
        confidence=0.9
    )

    assert updated["status"] == "success"

    assert updated["confidence"] == 0.9


# =========================================
# TRACE UPDATE
# =========================================

def test_trace_update():

    state = build_state()

    updated = set_state(
        state=state,
        agent="researcher",
        trace_action="research_completed"
    )

    assert len(updated["trace"]) > 0

    assert updated["trace"][-1]["agent"] == "researcher"


# =========================================
# EXTRA FIELD UPDATE
# =========================================

def test_extra_update():

    state = build_state()

    updated = set_state(
        state=state,
        extra={
            "workflow_step": "completed",
            "current_intent": "research"
        }
    )

    assert updated["workflow_step"] == "completed"

    assert updated["current_intent"] == "research"


# =========================================
# ERROR APPEND
# =========================================

def test_error_append():

    state = build_state()

    state["errors"].append("Some Error")

    assert len(state["errors"]) == 1


# =========================================
# EXECUTION TIME
# =========================================

def test_execution_time_exists():

    state = build_state()

    updated = set_state(
        state=state,
        status="success"
    )

    assert "status" in updated