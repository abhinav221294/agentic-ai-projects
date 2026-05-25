from src.workflows.state_management import AgentState
from src.workflows.state_management import set_state

from src.integrations.claude_client import claude_client_llm


from src.prompts.prompt import QUERY_HANDLING_PROMPT

from src.core.config import VALID_CATEGORIES,INTENT_CLASSIFICATION_COMPLETED,\
INTENT_CLASSIFICATION_FAILED
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query
)

from src.core.config import CLAUDE_MODEL


def query_handler(state: AgentState) -> AgentState:

    query = state.get("user_query")
    conversation_history = state.get("conversation_history")
    memory = state.get("memory")
    active_agent = "query_handler"

    if not validate_query(query):

        add_error(state, "Missing user query")

        return set_state(
        state=state,
        status="failed",
        agent=active_agent,
        trace_action="query_validation_failed",
        extra={
            "workflow_step": "query_validation_failed"
            }
        )

    try: 
        llm = claude_client_llm(model=CLAUDE_MODEL)

        prompt = f"""{QUERY_HANDLING_PROMPT}

User Query: {query}
"""
    
        intent = llm.invoke(prompt)

        response_text = str(intent.content).strip().lower()

        if not response_text:
            category = "none"
        else:
            category = response_text.split()[0]

        if category not in VALID_CATEGORIES:
            category = "none"
        
        workflow_step = INTENT_CLASSIFICATION_COMPLETED

        status = "success"

        print("CATEGORY:", category)


        add_trace(
            state,
            agent=active_agent,
            action=f"intent_detected:{category}"
        )

        return set_state(
        state,
        category=category,
        confidence=0.9,
        decision_source="llm_query_handler",
        status=status,
        agent=active_agent,
        trace_action=workflow_step,
        extra={
        "current_intent": category,
        "workflow_step": workflow_step
        }
    )
    
    except Exception as e:

        category = "none"
        workflow_step = INTENT_CLASSIFICATION_FAILED
        status = "failed"
        add_error(state, str(e))
        return set_state(
            state=state,
            category=category,
            status=status,
            agent=active_agent,
            trace_action=workflow_step,
            extra={
                "workflow_step": workflow_step
            }
        )



    