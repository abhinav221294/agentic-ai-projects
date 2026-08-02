from langgraph.graph import StateGraph, END
from src.workflows.state_management import AgentState,set_state
from src.agents.query_handler import query_handler
from src.agents.blog_writer_agent import blog_writer_agent,blog_writer_agent_stream
from src.agents.image_agent import image_agent
from src.agents.linkedin_writer_agent import linkedin_writer_agent, linkedin_writer_agent_stream
from src.agents.research_agent import research_agent
from src.agents.strategist_agent import strategist_agent
from src.agents.fallback_agent import fallback_agent
from src.agents.research_decision_agent import research_decision_agent
from src.core.config import WORKFLOW_STARTED,WORKFLOW_COMPLETED,WORKFLOW_FAILED

import time


def route_research(state: AgentState):

    if state.get("requires_research"):
        return "research"

    return "strategist"

def route_query(state: AgentState):

    intent = state.get("current_intent")

    if intent in ["blog", "linkedin"]:
        return "research_decision"

    elif intent == "image":
        return "image_generation"

    return "fallback"

def route_content(state: AgentState):

    intent = state.get("current_intent")

    if intent == "blog":
        return "blog_writer"

    elif intent == "linkedin":
        return "linkedin_writer"
    
    raise ValueError(f"Unsupported content intent: {intent}")

def content_dispatcher(state: AgentState):

    return state

def __build_workflow():


    workflow = StateGraph(AgentState)

    workflow.add_node("query_handler", query_handler)
    workflow.add_node("blog_writer", blog_writer_agent)
    workflow.add_node("linkedin_writer", linkedin_writer_agent)
    workflow.add_node("image_generation", image_agent)
    
    workflow.add_node("research_decision",research_decision_agent)
    
    workflow.add_node("research", research_agent)
    workflow.add_node("strategist", strategist_agent)
    workflow.add_node(
    "content_dispatcher",content_dispatcher)
    workflow.add_node("fallback", fallback_agent)

    workflow.set_entry_point("query_handler")

    workflow.add_conditional_edges(
    "query_handler",
    route_query,
    {
        "research_decision": "research_decision",
        "image_generation": "image_generation",
        "fallback": "fallback"
    }
)

    workflow.add_conditional_edges(
    "research_decision",
    route_research,
    {
        "research": "research",
        "strategist": "strategist"
    }
)

    #workflow.add_edge("blog_writer", END)
    workflow.add_edge("linkedin_writer", END)
    workflow.add_edge("image_generation", END)
    #workflow.add_edge("research", END)
    workflow.add_edge("research", "strategist")
    #workflow.add_edge("strategist", END)
    workflow.add_edge(
    "strategist",
    "content_dispatcher"
    )

    workflow.add_conditional_edges(
    "content_dispatcher",
    route_content,
    {
        "blog_writer": "blog_writer",
        "linkedin_writer": "linkedin_writer",
    }
    )
    
    workflow.add_edge("blog_writer", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()

workflow_app = __build_workflow()
def run_workflow(state: dict):

    start = time.time()

    try:
        # =========================
        # INITIAL STATE
        # =========================
        state["status"] = "running"
        state["workflow_step"] = WORKFLOW_STARTED

        result = workflow_app.invoke(state)
        
        #print("WORKFLOW_RESULT:", result)

        if result.get("status") == "failed":
            return result
        
        status="success"

        results =  set_state(
            state = result,
            start=start,
            answer=result.get("answer"),
            status=status,
            trace_action=WORKFLOW_COMPLETED
            )
        return results
    
    except Exception as e:
        #print("QUERY_HANDLER_ERROR:", repr(e))
        state.setdefault("errors", []).append(str(e))
        state["status"] = "failed"
        state["workflow_step"] = WORKFLOW_FAILED
        return state

    
def run_workflow_stream(state: AgentState):

    state["status"] = "running"
    state["workflow_step"] = WORKFLOW_STARTED

    try:
        intent = state.get("current_intent")

        if intent == "image":
            raise ValueError("Image streaming not supported")

        if intent not in ("blog", "linkedin"):
            raise ValueError(
                "Streaming only supported for content generation"
            )

        state = research_decision_agent(state)

        if route_research(state) == "research":
            state = research_agent(state)

        state = strategist_agent(state)

        route = route_content(state)

        if route == "blog_writer":
            yield from blog_writer_agent_stream(state)

        elif route == "linkedin_writer":
            yield from linkedin_writer_agent_stream(state)

    except Exception:
        state["status"] = "failed"
        state["workflow_step"] = WORKFLOW_FAILED
        raise



