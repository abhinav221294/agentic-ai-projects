from unittest.mock import patch

from backend.src.agents.linkedin_writer_agent import linkedin_writer_agent

from backend.src.core.config import (
    LINKEDIN_COMPLETED,
    LINKEDIN_FAILED,
    LINKEDIN_VALIDATION_FAILED
)


@patch("src.agents.linkedin_writer_agent.word_count_tool")
@patch("src.agents.linkedin_writer_agent.generate_cta_tool")
@patch("src.agents.linkedin_writer_agent.linkedin_hook_tool")
@patch("src.agents.linkedin_writer_agent.claude_client_llm")
def test_linkedin_writer_success(
    mock_llm,
    mock_hook,
    mock_cta,
    mock_word_count
):

    mock_hook.invoke.return_value = "Hook"
    mock_cta.invoke.return_value = "CTA"
    mock_word_count.invoke.return_value = 75

    mock_response = type(
        "MockResponse",
        (),
        {"content": "LinkedIn post"}
    )

    mock_llm.return_value.invoke.return_value = mock_response

    state = {
        "user_query": "Write a LinkedIn post on AI",
        "content_plan": "AI Plan",
        "errors": [],
        "trace": []
    }

    result = linkedin_writer_agent(state)

    assert result["status"] == "success"
    assert result["workflow_step"] == LINKEDIN_COMPLETED


def test_linkedin_writer_missing_query():

    state = {
        "user_query": "",
        "content_plan": "",
        "errors": [],
        "trace": []
    }

    result = linkedin_writer_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == LINKEDIN_VALIDATION_FAILED


@patch("src.agents.linkedin_writer_agent.claude_client_llm")
def test_linkedin_writer_exception(mock_llm):

    mock_llm.side_effect = Exception(
        "Claude Failed"
    )

    state = {
        "user_query": "AI LinkedIn",
        "content_plan": "Plan",
        "errors": [],
        "trace": []
    }

    result = linkedin_writer_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == LINKEDIN_FAILED


@patch("src.agents.linkedin_writer_agent.word_count_tool")
@patch("src.agents.linkedin_writer_agent.generate_cta_tool")
@patch("src.agents.linkedin_writer_agent.linkedin_hook_tool")
@patch("src.agents.linkedin_writer_agent.claude_client_llm")
def test_linkedin_writer_trace(
    mock_llm,
    mock_hook,
    mock_cta,
    mock_word_count
):

    mock_hook.invoke.return_value = "Hook"
    mock_cta.invoke.return_value = "CTA"
    mock_word_count.invoke.return_value = 50

    mock_response = type(
        "MockResponse",
        (),
        {"content": "LinkedIn content"}
    )

    mock_llm.return_value.invoke.return_value = mock_response

    state = {
        "user_query": "AI LinkedIn",
        "content_plan": "Plan",
        "errors": [],
        "trace": []
    }

    result = linkedin_writer_agent(state)

    assert len(result["trace"]) > 0