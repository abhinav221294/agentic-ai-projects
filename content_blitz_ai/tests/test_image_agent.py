import pytest
from unittest.mock import patch

from backend.src.agents.image_agent import image_agent

from backend.src.core.config import (
    IMAGE_COMPLETED,
    IMAGE_FAILED,
    IMAGE_VALIDATION_FAILED
)


@patch("src.agents.image_agent.generate_image")
def test_image_agent_success(mock_generate):

    mock_generate.return_value = (
        "https://test-image-url.com/image.png"
    )

    state = {
        "user_query": "Generate an image of a futuristic city",
        "errors": [],
        "trace": []
    }

    result = image_agent(state)

    assert result["status"] == "success"
    assert result["workflow_step"] == IMAGE_COMPLETED
    assert result["active_agent"] == "image_agent"
    assert result["answer"] is not None
    assert result["answer"] == (
        "https://test-image-url.com/image.png"
    )


def test_image_agent_missing_query():

    state = {
        "user_query": "",
        "errors": [],
        "trace": []
    }

    result = image_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == IMAGE_VALIDATION_FAILED


def test_image_agent_none_query():

    state = {
        "user_query": None,
        "errors": [],
        "trace": []
    }

    result = image_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == IMAGE_VALIDATION_FAILED


@patch("src.agents.image_agent.generate_image")
def test_image_agent_exception(mock_generate):

    mock_generate.side_effect = Exception(
        "Image API Failed"
    )

    state = {
        "user_query": "Create an AI robot",
        "errors": [],
        "trace": []
    }

    result = image_agent(state)

    assert result["status"] == "failed"
    assert result["workflow_step"] == IMAGE_FAILED


@patch("src.agents.image_agent.generate_image")
def test_image_agent_trace(mock_generate):

    mock_generate.return_value = (
        "https://test-image-url.com/image.png"
    )

    state = {
        "user_query": "Create a mountain landscape",
        "errors": [],
        "trace": []
    }

    result = image_agent(state)

    assert len(result["trace"]) > 0