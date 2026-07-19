from src.agents.query_handler import query_handler
from src.core.router import route_workflow


def run_workflow(state):

    state = query_handler(state)
    print("RUN_WORKFLOW START")
    if state["status"] == "failed":
        return state

    state = route_workflow(state)

    return state