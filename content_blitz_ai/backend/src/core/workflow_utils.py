import time
from typing import Any, Dict

def add_trace(state: Dict, agent: str, action: str,  **metadata):

    state["trace"].append({
        "trace_id": state.get("trace_id"),
        "agent": agent,
        "action": action,
        "timestamp": time.time(),
         **metadata
    })

    return state


def add_error(state: Dict, error_message: str):

    state["errors"].append(error_message)

    return state


def validate_query(query):

    if not query:
        return False

    return True


def invoke_tool_with_trace(
    state: dict,
    tool: Any,
    tool_input: dict,
    agent: str,
    operation: str,
):
    start = time.time()

    try:
        result = tool.invoke(tool_input)

        latency = round(time.time() - start, 3)

        state.setdefault("trace", []).append({
            "trace_id": state.get("trace_id"),
            "agent": agent,
            "action": "tool_call",
            "operation": operation,
            "timestamp": time.time(),
            "latency": latency,
            "status": "success",
        })

        return result

    except Exception as e:

        latency = round(time.time() - start, 3)

        state.setdefault("trace", []).append({
            "trace_id": state.get("trace_id"),
            "agent": agent,
            "action": "tool_call",
            "operation": operation,
            "timestamp": time.time(),
            "latency": latency,
            "status": "failed",
            "error": str(e),
        })

        raise

def add_request_cost(state: dict) -> dict:

    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    total_cost = 0.0

    for entry in state.get("trace", []):

        if entry.get("action") not in {
            "llm_call",
            "llm_stream",
        }:
            continue

        input_tokens += entry.get("input_tokens", 0)
        output_tokens += entry.get("output_tokens", 0)
        total_tokens += entry.get("total_tokens", 0)
        total_cost += entry.get("cost", 0.0)

    state.setdefault("metadata", {})["llm_usage"] = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 8),
    }

    print("\n========== REQUEST COST ==========")
    print("Total LLM Cost:", total_cost)
    print("==================================\n")
    
    return state