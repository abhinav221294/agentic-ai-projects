from src.agents.fallback_agent import fallback_agent


def create_mock_state():

    return {
        "user_id": "test_user",
        "session_id": "session_001",
        "user_query": "random unsupported query",
        "conversation_history": [],
        "memory": [],
        "errors": [],
        "trace": [],
        "tool_outputs": {},
        "generated_assets": [],
        "execution_logs": [],
        "metadata": {},
        "status": "running",
        "retry_count": 0
    }


def test_fallback_agent_success():

    # =========================
    # CREATE MOCK STATE
    # =========================

    state = create_mock_state()

    # =========================
    # RUN AGENT
    # =========================

    updated_state = fallback_agent(state)

    # =========================
    # ASSERTIONS
    # =========================

    assert updated_state["status"] == "success"

    assert updated_state["active_agent"] == "fallback_agent"

    assert updated_state["workflow_step"] == "fallback_completed"

    assert "Sorry" in updated_state["answer"]

    assert len(updated_state["trace"]) > 0