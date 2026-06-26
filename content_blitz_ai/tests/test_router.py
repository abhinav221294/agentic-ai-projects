from src.core.router import route_workflow
from unittest.mock import patch

def test_route_to_blog():
    state = {"current_intent": "blog"}

@patch("src.core.router.blog_writer_agent")
def test_route_blog(mock_blog):

    state = {
        "current_intent": "blog"
    }

    route_workflow(state)

    mock_blog.assert_called_once_with(state)


@patch("src.core.router.linkedin_writer_agent")
def test_route_blog(mock_linkedin):

    state = {
        "current_intent": "linkedin"
    }

    route_workflow(state)

    mock_linkedin.assert_called_once_with(state)


@patch("src.core.router.research_agent")
def test_route_blog(mock_research):

    state = {
        "current_intent": "research"
    }

    route_workflow(state)

    mock_research.assert_called_once_with(state)


@patch("src.core.router.image_agent")
def test_route_blog(mock_image):

    state = {
    "current_intent": "image",
    "trace": [],
    "errors": []
    }

    route_workflow(state)

    mock_image.assert_called_once_with(state)


@patch("src.core.router.fallback_agent")
def test_route_fallback(mock_fallback):

    state = {"current_intent": "unknown",
             "trace": [],
             "errors": []}
    

    route_workflow(state)

    mock_fallback.assert_called_once_with(state)