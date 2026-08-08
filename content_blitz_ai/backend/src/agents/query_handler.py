from src.workflows.state_management import AgentState
from src.workflows.state_management import set_state

from src.integrations.claude_client import claude_client_llm


from src.prompts.prompt import QUERY_HANDLING_PROMPT

from src.core.config import (VALID_CATEGORIES,INTENT_CLASSIFICATION_COMPLETED,
INTENT_CLASSIFICATION_FAILED, LOW_CONFIDENCE, HIGH_CONFIDENCE,QUERY_VALIDATION_FAILED)
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query
)
from src.core.llm_service import LLMService

from src.core.config import CLAUDE_MODEL
import time

def query_handler(state: AgentState) -> AgentState:
    start = time.time()
    query = state.get("user_query")

    # Reserved for future conversational memory support
    #conversation_history = state.get("conversation_history")
    #memory = state.get("memory")
    conversation_history = state.get(
    "conversation_history",
    []
     )

    retrieved_memories = state.get(
    "retrieved_memories",
    []
    )
    
    
    active_agent = "query_handler"
    #print("QUERY_HANDLER START")
    if not validate_query(query):

        add_error(state, "Missing user query")
        add_trace(
        state,
        agent=active_agent,
        action=QUERY_VALIDATION_FAILED
        )
        return set_state(
        state=state,
        status="failed",
        agent=active_agent,
        trace_action=QUERY_VALIDATION_FAILED,
        extra={
            "workflow_step": QUERY_VALIDATION_FAILED
            }
        )

    try: 
        llm = claude_client_llm(model=CLAUDE_MODEL)

        prompt = f"""{QUERY_HANDLING_PROMPT}

User Query: {query}
"""
    
        intent = LLMService.invoke(
            llm=llm,
            prompt=prompt,
            state=state,
            agent=active_agent,
            operation="intent_classification"
        )

        response_text = str(
        intent.content
        ).strip().lower()

        category = (
        response_text.split(maxsplit=1)[0]
        if response_text
        else "none"
        )

        if category not in VALID_CATEGORIES:
            category = "none"
        
        workflow_step = INTENT_CLASSIFICATION_COMPLETED

        status = "success"


        add_trace(
            state,
            agent=active_agent,
            action=f"intent_detected:{category}"
        )
        execution_time = round(time.time() - start, 2)
        return set_state(
        state,
        category=category,
        confidence=HIGH_CONFIDENCE,
        decision_source="llm_query_handler",
        status=status,
        agent=active_agent,
        trace_action=workflow_step,
        extra={
        "current_intent": category,
        "workflow_step": workflow_step,
        "execution_time": execution_time
        }
    )
    
    except Exception as e:
        #print("QUERY_HANDLER ERROR:", repr(e))
        execution_time = round(time.time() - start, 2)
        category = "none"
        workflow_step = INTENT_CLASSIFICATION_FAILED
        status = "failed"
        add_error(state, str(e))
        
        add_trace(
        state,
        active_agent,
        workflow_step
        )
        return set_state(
            state=state,
            category=category,
            confidence=LOW_CONFIDENCE,
            status=status,
            agent=active_agent,
            trace_action=workflow_step,
            extra={
                "workflow_step": workflow_step,
                "execution_time": execution_time
            }
        )



    