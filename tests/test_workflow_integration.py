from src.workflows.content_workflow import run_workflow


def test_research_workflow():

    state = {
        "user_id": "test_user",
        "session_id": "session_001",
        "user_query": "Research latest AI agent frameworks",
        "conversation_history": [],
        "memory": [],
        "errors": [],
        "trace": []
    }

    result = run_workflow(state)

    assert result["status"] == "success"

    assert result["current_intent"] == "research"

    assert result["workflow_step"] == "research_completed"

    assert result["answer"] is not None