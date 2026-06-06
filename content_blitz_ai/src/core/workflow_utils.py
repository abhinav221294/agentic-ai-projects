import time
from typing import Dict


def add_trace(state: Dict, agent: str, action: str):

    state["trace"].append({
        "agent": agent,
        "action": action,
        "timestamp": time.time()
    })

    return state


def add_error(state: Dict, error_message: str):

    state["errors"].append(error_message)

    return state


def validate_query(query):

    if not query:
        return False

    return True