from src.core.workflow_utils import add_request_cost


def test_request_cost_aggregation():

    state = {
        "trace": [
            {
                "action": "llm_call",
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
                "cost": 0.001,
            },
            {
                "action": "tool_call",
                "cost": 0.500,
            },
            {
                "action": "llm_stream",
                "input_tokens": 200,
                "output_tokens": 100,
                "total_tokens": 300,
                "cost": 0.002,
            },
        ]
    }

    add_request_cost(state)

    usage = state["metadata"]["llm_usage"]

    assert usage["input_tokens"] == 300
    assert usage["output_tokens"] == 150
    assert usage["total_tokens"] == 450
    assert usage["total_cost"] == 0.003