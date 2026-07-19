# =========================
# IMPORTS
# =========================

# pytest is used for writing and running test cases
import pytest


# patch:
# temporarily replaces real functions/classes during testing

# MagicMock:
# creates fake/mock objects for simulating behavior

from unittest.mock import patch, MagicMock


# importing the main workflow execution function
# this is the workflow we are testing

from backend.src.workflows.content_workflow import run_workflow


# =========================
# BASE TEST STATE
# =========================

# helper function that creates a default workflow state

# every workflow execution requires a state dictionary
# this function ensures consistent test input structure

def build_state(query="Test Query"):

    return {

        # unique user identifier
        "user_id": "test_user",

        # workflow session id
        "session_id": "session_001",

        # actual user query
        "user_query": query,

        # previous conversations
        "conversation_history": [],

        # long-term memory
        "memory": [],

        # stores workflow errors
        "errors": [],

        # workflow execution trace
        "trace": [],

        # stores tool/API outputs
        "tool_outputs": {},

        # generated assets/files/images
        "generated_assets": [],

        # workflow logs
        "execution_logs": [],

        # metadata/configuration
        "metadata": {},

        # retry counter for failures
        "retry_count": 0
    }


# =========================================
# EMPTY QUERY TEST
# =========================================

# tests how workflow behaves
# when user provides empty query

def test_empty_query():

    # create state with empty query
    state = build_state(query="")

    # execute workflow
    result = run_workflow(state)

    # workflow should not crash
    # it may either:
    # - fail gracefully
    # - handle fallback successfully

    assert result["status"] in ["failed", "success"]


# =========================================
# MISSING QUERY FIELD TEST
# =========================================

# tests missing required field scenario

def test_missing_query_field():

    # create valid state first
    state = build_state()

    # remove required key manually
    del state["user_query"]

    # run workflow
    result = run_workflow(state)

    # workflow should fail gracefully
    assert result["status"] == "failed"

    # errors list should contain exception/error info
    assert len(result["errors"]) > 0


# =========================================
# TAVILY API FAILURE TEST
# =========================================

# patch replaces real tavily_search function
# with mocked version

@patch("src.agents.research_agent.tavily_search")
def test_tavily_failure(mock_tavily):

    # simulate API exception
    mock_tavily.side_effect = Exception("Tavily API Failure")

    # research-related query
    state = build_state(
        query="Research latest AI agent frameworks"
    )

    # execute workflow
    result = run_workflow(state)

    # workflow should fail gracefully
    assert result["status"] == "failed"

    # errors should be captured
    assert len(result["errors"]) > 0


# =========================================
# CLAUDE API FAILURE TEST
# =========================================

# patch replaces real Claude LLM client

@patch("src.agents.query_handler.claude_client_llm")
def test_claude_failure(mock_llm):

    # create fake/mock model
    mock_model = MagicMock()

    # simulate Claude invoke() failure
    mock_model.invoke.side_effect = Exception(
        "Claude API Failure"
    )

    # replace real LLM with mocked one
    mock_llm.return_value = mock_model

    # research query
    state = build_state(
        query="Research AI agents"
    )

    # execute workflow
    result = run_workflow(state)

    # workflow should fail safely
    assert result["status"] == "failed"

    # errors should be logged
    assert len(result["errors"]) > 0


# =========================================
# INVALID STATE TYPE TEST
# =========================================

# tests completely invalid input type

def test_invalid_state_type():

    # instead of dictionary,
    # passing string intentionally

    state = "invalid_state"

    # pytest.raises checks whether exception occurs

    with pytest.raises(Exception):

        # workflow should raise exception
        run_workflow(state)


# =========================================
# VERY LARGE QUERY TEST
# =========================================

# tests scalability and robustness
# against huge user input

def test_large_query():

    # generates extremely long query
    # "AI AI AI AI ..." repeated 5000 times

    huge_query = "AI " * 5000

    # create workflow state
    state = build_state(query=huge_query)

    # execute workflow
    result = run_workflow(state)

    # workflow should not crash unexpectedly
    # either success or controlled failure acceptable

    assert result["status"] in ["success", "failed"]


# =========================================
# SPECIAL CHARACTERS QUERY TEST
# =========================================

# tests how workflow handles noisy/suspicious input

def test_special_characters_query():

    # query containing unusual symbols
    state = build_state(
        query="@@@@ #### $$$$ AI agents ????"
    )

    # execute workflow
    result = run_workflow(state)

    # workflow should remain stable
    assert result["status"] in ["success", "failed"]