from unittest.mock import patch
import pytest
from backend.src.workflows.content_workflow import run_workflow

@patch("src.workflows.content_workflow.blog_writer_agent")
@patch("src.workflows.content_workflow.strategist_agent")
@patch("src.workflows.content_workflow.research_agent")
@patch("src.workflows.content_workflow.query_handler")
def test_blog_with_research(
    mock_query,
    mock_research,
    mock_strategy,
    mock_blog
):

    state = {
        "user_query": "Write a blog on latest AI trends",
        "trace": [],
        "errors": []
    }

    mock_query.return_value = {
        **state,
        "current_intent": "blog",
        "status": "success"
    }

    mock_research.return_value = {
        **state,
        "answer": "research content",
        "status": "success"
    }

    mock_strategy.return_value = {
        **state,
        "content_plan": "strategy",
        "status": "success"
    }

    mock_blog.return_value = {
        **state,
        "answer": "blog output",
        "status": "success"
    }

    result = run_workflow(state)

    assert result["status"] == "success"


@patch("src.workflows.content_workflow.research_decision_agent")
def test_blog_without_research(
    mock_decision
):

    state = {
        "user_query": "Write a blog on Python generators",
        "trace": [],
        "errors": []
    }

    mock_decision.return_value = {
        **state,
        "requires_research": False
    }

    result = run_workflow(state)

    assert result is not None



def test_linkedin_with_research():

    state = {
        "user_query": "Create a LinkedIn post on latest OpenAI release",
        "trace": [],
        "errors": []
    }

    result = run_workflow(state)

    assert result is not None


def test_linkedin_without_research():

    state = {
        "user_query": "Create a LinkedIn post on leadership",
        "trace": [],
        "errors": []
    }

    result = run_workflow(state)

    assert result is not None

@patch(
    "src.workflows.content_workflow.research_agent"
)
def test_research_workflow(
    mock_research
):

    state = {
        "user_query": "Research Azure AI Foundry",
        "trace": [],
        "errors": []
    }

    mock_research.return_value = {
        **state,
        "status": "success",
        "answer": "research output"
    }

    result = run_workflow(state)

    assert result["status"] == "success"

@patch(
    "src.workflows.content_workflow.fallback_agent"
)


def test_fallback_workflow(
    mock_fallback
):

    state = {
        "user_query": "asdfasdfasdf",
        "trace": [],
        "errors": []
    }

    mock_fallback.return_value = {
        **state,
        "status": "success",
        "answer": "fallback"
    }

    result = run_workflow(state)

    assert result["status"] == "success"

@pytest.mark.skip(
    reason="Agent failure handled in agent-level tests"
)
def test_query_handler_failure():
    pass