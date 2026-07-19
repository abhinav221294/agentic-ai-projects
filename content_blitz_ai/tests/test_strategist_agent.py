from unittest.mock import patch, MagicMock

from backend.src.agents.strategist_agent import strategist_agent


def create_mock_state():

    return {
        "user_query": "Write a blog about AI agents",
        "answer": "AI agents are transforming startups through automation.",
        "category": "blog",

        # Required state fields
        "errors": [],
        "trace": [],
        "messages": [],
        "conversation_history": [],
        "memory": [],
        "sources": [],
        "tool_outputs": {},
        "generated_assets": [],
        "execution_logs": [],
        "retry_count": 0,
        "metadata": {}
    }


@patch("src.agents.strategist_agent.gemini_llm_client")
def test_strategist_agent_success(mock_llm_client):

    # =========================
    # MOCK LLM RESPONSE
    # =========================

    mock_llm = MagicMock()

    mock_response = MagicMock()

    mock_response.content = """
    {
        "title": "AI Agents for Startups",
        "target_audience": "Startup founders",
        "tone": "Professional",
        "sections": ["Introduction", "Benefits", "Conclusion"]
    }
    """

    mock_llm.invoke.return_value = mock_response

    mock_llm_client.return_value = mock_llm

    # =========================
    # RUN AGENT
    # =========================

    state = create_mock_state()

    updated_state = strategist_agent(state)

    # =========================
    # ASSERTIONS
    # =========================

    assert updated_state["status"] == "success"

    assert updated_state["active_agent"] == "strategist_agent"

    assert "content_plan" in updated_state

    assert updated_state["content_plan"] is not None

    assert updated_state["workflow_step"] == "strategy_completed"


@patch("src.agents.strategist_agent.gemini_llm_client")
def test_strategist_agent_failure(mock_llm_client):

    # =========================
    # FORCE EXCEPTION
    # =========================

    mock_llm = MagicMock()

    mock_llm.invoke.side_effect = Exception("LLM Failure")

    mock_llm_client.return_value = mock_llm

    # =========================
    # RUN AGENT
    # =========================

    state = create_mock_state()

    updated_state = strategist_agent(state)

    # =========================
    # ASSERTIONS
    # =========================

    assert updated_state["status"] == "failed"

    assert updated_state["active_agent"] == "strategist_agent"

    assert len(updated_state["errors"]) > 0

    assert updated_state["workflow_step"] == "strategy_failed"