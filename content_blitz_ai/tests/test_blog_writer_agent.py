from unittest.mock import patch

from src.agents.blog_writer_agent import blog_writer_agent

from src.core.config import (
    BLOG_COMPLETED,
    BLOG_FAILED,
    BLOG_VALIDATION_FAILED
)


@patch("src.agents.blog_writer_agent.word_count_tool")
@patch("src.agents.blog_writer_agent.blog_outline_tool")
@patch("src.agents.blog_writer_agent.generate_title_tool")
@patch("src.agents.blog_writer_agent.claude_client_llm")
def test_blog_writer_success(
    mock_llm,
    mock_title,
    mock_outline,
    mock_word_count
):

    mock_title.invoke.return_value = "AI Title"
    mock_outline.invoke.return_value = "AI Outline"
    mock_word_count.invoke.return_value = 250

    mock_response = type(
        "MockResponse",
        (),
        {"content": "Generated blog content"}
    )

    mock_llm.return_value.invoke.return_value = mock_response

    state = {
        "user_query": "Write a blog about AI",
        "content_plan": "AI Strategy",
        "errors": [],
        "trace": []
    }

    result = blog_writer_agent(state)

    assert result["status"] == "success"
    assert result["workflow_step"] == BLOG_COMPLETED


def test_blog_writer_missing_query():

    state = {
        "user_query": "",
        "content_plan": "",
        "errors": [],
        "trace": []
    }

    result = blog_writer_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == BLOG_VALIDATION_FAILED


@patch("src.agents.blog_writer_agent.claude_client_llm")
def test_blog_writer_exception(mock_llm):

    mock_llm.side_effect = Exception(
        "LLM Failed"
    )

    state = {
        "user_query": "AI Blog",
        "content_plan": "Plan",
        "errors": [],
        "trace": []
    }

    result = blog_writer_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == BLOG_FAILED


@patch("src.agents.blog_writer_agent.word_count_tool")
@patch("src.agents.blog_writer_agent.blog_outline_tool")
@patch("src.agents.blog_writer_agent.generate_title_tool")
@patch("src.agents.blog_writer_agent.claude_client_llm")
def test_blog_writer_trace(
    mock_llm,
    mock_title,
    mock_outline,
    mock_word_count
):

    mock_title.invoke.return_value = "Title"
    mock_outline.invoke.return_value = "Outline"
    mock_word_count.invoke.return_value = 100

    mock_response = type(
        "MockResponse",
        (),
        {"content": "Blog"}
    )

    mock_llm.return_value.invoke.return_value = mock_response

    state = {
        "user_query": "AI Blog",
        "content_plan": "Plan",
        "errors": [],
        "trace": []
    }

    result = blog_writer_agent(state)

    assert len(result["trace"]) > 0