from unittest.mock import patch, MagicMock

from src.agents.research_agent import (
    optimize_search_query,
    format_search_results,
    synthesize_research,
    research_agent
)


# =========================================
# MOCK RESPONSE
# =========================================

class MockResponse:

    def __init__(self, text):

        self.content = text


# =========================================
# BASE STATE
# =========================================

def build_state():

    return {
        "user_id": "test_user",
        "session_id": "session_001",
        "user_query": "Research latest AI agent frameworks",
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
# QUERY OPTIMIZATION
# =========================================

def test_optimize_search_query():

    mock_llm = MagicMock()

    mock_llm.invoke.return_value = MockResponse(
        "latest AI agent frameworks 2026"
    )

    result = optimize_search_query(
        query="Research latest AI agent frameworks",
        llm=mock_llm
    )

    assert isinstance(result, str)

    assert len(result) > 0


# =========================================
# FORMAT SEARCH RESULTS
# =========================================

def test_format_search_results():

    mock_results = {
        "results": [
            {
                "title": "LangGraph",
                "content": "LangGraph enables stateful agents",
                "url": "https://example.com"
            }
        ]
    }

    formatted = format_search_results(mock_results)

    assert "LangGraph" in formatted

    assert "https://example.com" in formatted


# =========================================
# SYNTHESIS
# =========================================

def test_synthesize_research():

    mock_llm = MagicMock()

    mock_llm.invoke.return_value = MockResponse(
        "AI agent frameworks are rapidly evolving."
    )

    result = synthesize_research(
        user_query="AI agent frameworks",
        formatted_results="Some retrieved content",
        llm=mock_llm
    )

    assert isinstance(result, str)

    assert len(result) > 0


# =========================================
# FULL RESEARCH AGENT
# =========================================

@patch("src.agents.research_agent.tavily_search")
@patch("src.agents.research_agent.gemini_llm_client")
def test_research_agent_success(
    mock_claude,
    mock_tavily
):

    # =========================
    # MOCK LLM
    # =========================

    mock_model = MagicMock()

    mock_model.invoke.side_effect = [

        MockResponse(
            "latest AI agent frameworks 2026"
        ),

        MockResponse(
            "LangGraph and CrewAI are popular frameworks."
        )
    ]

    mock_claude.return_value = mock_model

    # =========================
    # MOCK SEARCH
    # =========================

    mock_tavily.return_value = {
        "results": [
            {
                "title": "LangGraph",
                "content": "LangGraph is powerful",
                "url": "https://example.com"
            }
        ]
    }

    state = build_state()

    result = research_agent(state)

    assert result["status"] == "success"

    assert result["workflow_step"] == "research_completed"

    assert result["answer"] is not None

    assert result["active_agent"] == "researcher"


# =========================================
# RESEARCH FAILURE
# =========================================

@patch("src.agents.research_agent.tavily_search")
def test_research_agent_failure(mock_tavily):

    mock_tavily.side_effect = Exception(
        "Tavily Failure"
    )

    state = build_state()

    result = research_agent(state)

    assert result["status"] == "failed"

    assert len(result["errors"]) > 0