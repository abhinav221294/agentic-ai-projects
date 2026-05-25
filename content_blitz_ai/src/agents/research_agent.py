from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import RESEARCH_PROMPT, RESEARCH_SYNTHESIS_PROMPT
#from src.integrations.perplexity_client import perplexity_search
from src.integrations.tavily_client import tavily_search
from src.integrations.gemini_client import gemini_llm_client
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query
)
from src.core.config import GEMINI_MODEL,RESEARCH_COMPLETED,RESEARCH_FAILED
import time

def optimize_search_query(query, llm):

    prompt = f"""{RESEARCH_PROMPT}

User Query:
{query}"""

    response = llm.invoke(prompt)

    if isinstance(response.content, list):

        optimized_query = " ".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        ).strip()

    else:
        optimized_query = str(response.content).strip()

    return optimized_query

def format_search_results(search_results):

    formatted_results = []

    for result in search_results.get("results", []):

        formatted_results.append(
            f"""Title:
{result.get("title")}

Content:
{result.get("content", "")[:1000]}

Source:
{result.get("url")}"""
        )

    return "\n\n".join(formatted_results)



def synthesize_research(user_query, formatted_results, llm):
    prompt = f"""{RESEARCH_SYNTHESIS_PROMPT}

User Query:
{user_query}

Retrieved Research:
{formatted_results}"""
    
    response = llm.invoke(prompt)

    if isinstance(response.content, list):

        final_answer = " ".join(
            block.text
            for block in response.content
                if hasattr(block, "text")
        ).strip()

    else:
        final_answer = str(response.content).strip()
    
    return final_answer



def research_agent(state: AgentState) -> AgentState:

    start = time.time()
    
    query = state.get("user_query")

    if not validate_query(query):

        add_error(state, "Missing research query")

        return set_state(
        state=state,
        status="failed",
        agent="researcher",
        trace_action=RESEARCH_FAILED,
        extra={
            "workflow_step": RESEARCH_FAILED
            }
        )

    active_agent = "researcher"

    try:
        add_trace(state, active_agent, "query_optimization_started")
        llm = gemini_llm_client(model=GEMINI_MODEL)

        # =========================
        # QUERY OPTIMIZATION
        # =========================

        query_modified = optimize_search_query(
            query=query,
            llm=llm
        )
        add_trace(state, active_agent, "query_optimization_completed")
        # =========================
        # RETRIEVAL
        # =========================

        search_results = tavily_search(
            query=query_modified
        )

        add_trace(state, active_agent, "retrieval_completed")

         # =========================
        # FORMAT RESULTS
        # =========================

        formatted_results = format_search_results(
            search_results
        )

        if not formatted_results:

            add_error(state, "No research results found")

            return set_state(
                state=state,
                status="failed",
                confidence=0.2,
                agent=active_agent,
                trace_action=RESEARCH_FAILED,
                extra={
                    "workflow_step": RESEARCH_FAILED
                }
            )

        # =========================
        # SYNTHESIS
        # =========================

        synthesized_answer = synthesize_research(
            user_query=query,
            formatted_results=formatted_results,
            llm=llm
            )
        
        add_trace(state, active_agent, "synthesis_completed")
        
        add_trace(
        state,
        agent=active_agent,
        action=RESEARCH_COMPLETED
        )

        return set_state(
            state=state,
            start=start,
            confidence=min(len(search_results.get("results", [])) / 5, 1.0),
            status="success",
            agent=active_agent,
            trace_action=RESEARCH_COMPLETED,
            extra={
                "optimized_query": query_modified,
                "research_data": search_results,
                "workflow_step": RESEARCH_COMPLETED,
                "execution_time": round(time.time() - start, 2)
            },
            answer=synthesized_answer
        )

    except Exception as e:

        add_error(state, str(e))

        return set_state(
            state=state,
            start=start,
            confidence=0.2,
            status="failed",
            agent=active_agent,
            trace_action=RESEARCH_FAILED,
            extra={
                "workflow_step": RESEARCH_FAILED
            }
        )
