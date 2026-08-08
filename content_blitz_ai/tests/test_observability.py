from src.core.llm_service import LLMService
from src.core.workflow_utils import invoke_tool_with_trace


class FakeLLMResponse:
    content = "Hello from fake LLM"
    response_metadata = {
        "model_name": "fake-model"
    }


class FakeLLM:

    def invoke(self, prompt):
        return FakeLLMResponse()


class FakeTool:

    name = "fake_tool"

    def invoke(self, tool_input):
        return {
            "result": "success"
        }


class FailingTool:

    name = "failing_tool"

    def invoke(self, tool_input):
        raise ValueError("Tool failed")


def test_llm_trace():

    state = {
        "trace_id": "test-trace-123",
        "trace": []
    }

    llm = FakeLLM()

    response = LLMService.invoke(
        llm=llm,
        prompt="Hello",
        state=state,
        agent="test_agent",
        operation="test_llm",
    )

    assert response.content == "Hello from fake LLM"

    assert len(state["trace"]) == 1

    trace = state["trace"][0]

    assert trace["trace_id"] == "test-trace-123"
    assert trace["agent"] == "test_agent"
    assert trace["action"] == "llm_call"
    assert trace["operation"] == "test_llm"
    assert trace["status"] == "success"
    assert trace["latency"] >= 0


def test_tool_trace():

    state = {
        "trace_id": "test-trace-456",
        "trace": []
    }

    tool = FakeTool()

    result = invoke_tool_with_trace(
        state=state,
        tool=tool,
        tool_input={"query": "hello"},
        agent="test_agent",
        operation="test_tool",
    )

    assert result["result"] == "success"

    assert len(state["trace"]) == 1

    trace = state["trace"][0]

    assert trace["trace_id"] == "test-trace-456"
    assert trace["agent"] == "test_agent"
    assert trace["action"] == "tool_call"
    assert trace["operation"] == "test_tool"
    assert trace["status"] == "success"
    assert trace["latency"] >= 0


def test_failed_tool_trace():

    state = {
        "trace_id": "test-trace-789",
        "trace": []
    }

    tool = FailingTool()

    try:
        invoke_tool_with_trace(
            state=state,
            tool=tool,
            tool_input={},
            agent="test_agent",
            operation="failing_tool",
        )
    except ValueError:
        pass

    assert len(state["trace"]) == 1

    trace = state["trace"][0]

    assert trace["trace_id"] == "test-trace-789"
    assert trace["action"] == "tool_call"
    assert trace["operation"] == "failing_tool"
    assert trace["status"] == "failed"
    assert trace["error"] == "Tool failed"


def test_llm_stream_trace():

    state = {
        "trace_id": "test-stream-123",
        "trace": []
    }

    class FakeStreamLLM:

        def stream(self, prompt):
            yield FakeLLMResponse()
            yield FakeLLMResponse()

    chunks = list(
        LLMService.stream(
            llm=FakeStreamLLM(),
            prompt="Hello",
            state=state,
            agent="test_agent",
            operation="test_stream",
        )
    )

    assert len(chunks) == 2

    assert len(state["trace"]) == 1

    trace = state["trace"][0]

    assert trace["trace_id"] == "test-stream-123"
    assert trace["agent"] == "test_agent"
    assert trace["action"] == "llm_stream"
    assert trace["operation"] == "test_stream"
    assert trace["status"] == "success"
    assert trace["latency"] >= 0
    assert trace["time_to_first_token"] >= 0
    assert trace["output_length"] > 0