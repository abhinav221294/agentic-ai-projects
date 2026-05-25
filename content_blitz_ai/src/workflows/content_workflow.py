from langgraph.graph import StateGraph, END
from src.workflows.state_management import AgentState,set_state
from src.agents.query_handler import query_handler
from src.agents.blog_writer_agent import blog_writer_agent
from src.agents.image_agent import image_agent
from src.agents.linkedin_writer_agent import linkedin_writer_agent
from src.agents.research_agent import research_agent
from src.agents.strategist_agent import strategist_agent
from src.agents.fallback_agent import fallback_agent
import time

def route_query(state: AgentState):

    intent = state.get("current_intent")

    if intent == "blog":
        return "research"

    elif intent == "linkedin":
        return "linkedin_writer"

    elif intent == "image":
        return "image_generation"

    elif intent == "research":
        return "research"

    elif intent == "strategy":
        return "strategist"

    return "fallback"

def __build_workflow():


    workflow = StateGraph(AgentState)

    workflow.add_node("query_handler", query_handler)
    workflow.add_node("blog_writer", blog_writer_agent)
    workflow.add_node("linkedin_writer", linkedin_writer_agent)
    workflow.add_node("image_generation", image_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("strategist", strategist_agent)
    workflow.add_node("fallback", fallback_agent)

    workflow.set_entry_point("query_handler")

    workflow.add_conditional_edges("query_handler",
                                   route_query)

    #workflow.add_edge("blog_writer", END)
    workflow.add_edge("linkedin_writer", END)
    workflow.add_edge("image_generation", END)
    #workflow.add_edge("research", END)
    workflow.add_edge("research", "strategist")
    #workflow.add_edge("strategist", END)
    workflow.add_edge("strategist", "blog_writer")
    workflow.add_edge("blog_writer", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()

def run_workflow(state: dict):

    start = time.time()

    try:
        # =========================
        # INITIAL STATE
        # =========================
        state["status"] = "running"
        state["workflow_step"] = "workflow_started"

    
        workflow_app = __build_workflow()
     
        result = workflow_app.invoke(state)
        
        print("WORKFLOW_RESULT:", result)

        if result.get("status") == "failed":
            return result
        
        status="success"

        results =  set_state(
            state = result,
            start=start,
            answer=result.get("answer"),
            status=status,
            trace_action="workflow_completed"
            )
        return results
    
    except Exception as e:
        print("QUERY_HANDLER_ERROR:", repr(e))
        state.setdefault("errors", []).append(str(e))
        state["status"] = "failed"
        state["workflow_step"] = "workflow_failed"
        return state

    





