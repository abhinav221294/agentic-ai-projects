from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import (
    RESEARCH_QUERY_OPTIMIZER_PROMPT,
    RESEARCH_SYNTHESIS_PROMPT,
    GLOBAL_GUARDRAILS
)
#from src.integrations.perplexity_client import perplexity_search
#from src.integrations.tavily_client import tavily_search
from src.integrations.gemini_client import gemini_llm_client
from src.tools.research_tools import web_search_tool
from src.core.workflow_utils import (
    add_trace,
    add_error,
    validate_query,
    invoke_tool_with_trace
)
from src.core.llm_service import LLMService

from src.core.config import (GEMINI_MODEL,RESEARCH_COMPLETED,
RESEARCH_FAILED,LOW_CONFIDENCE, SYNTHESIS_COMPLETED,RETRIEVAL_COMPLETED,
QUERY_OPTIMIZATION_STARTED,QUERY_OPTIMIZATION_COMPLETED)
import time

def optimize_search_query(query, llm, state):

    prompt = f"""
{RESEARCH_QUERY_OPTIMIZER_PROMPT}

User Request:
{query}
"""

    response = LLMService.invoke(
        llm=llm,
        state=state,
        prompt=prompt,
        agent="research_agent",
        operation="query_optimization"
    )

    if isinstance(response.content, list):

        content = " ".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        ).strip()

    else:
        content = str(response.content).strip()

    print("\n========== OPTIMIZER RESPONSE ==========")
    print(content)
    print("========================================\n")

    search_queries = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    if not search_queries:
        raise ValueError(
        "Research query optimizer returned no queries"
        )

    search_queries = search_queries[:3]

    return search_queries

def format_search_results(search_results):

    formatted_results = []

    for i, result in enumerate(
        search_results.get("results", []),
        start=1
    ):

        content = result.get("content", "")
        citations = result.get("citations", [])

        formatted_results.append(
            f"""
RESEARCH SOURCE {i}

Title:
{result.get("title", "Unknown")}

Content:
{content[:5000]}

Citations:
{chr(10).join(citations[:10])}
"""
        )

    return "\n\n".join(formatted_results)


def synthesize_research(user_query, formatted_results, llm, state):
    prompt = f"""{GLOBAL_GUARDRAILS}

{RESEARCH_SYNTHESIS_PROMPT}

User Query:
{user_query}

Retrieved Research:
{formatted_results}"""
    
    response = LLMService.invoke(
    state=state,
    llm=llm,
    prompt=prompt,
    agent="research_agent",
    operation="research_synthesis",
    )
    metadata = getattr(response, "metadata", {})
    print("METADATA:", metadata)

    if isinstance(response.content, list):

        final_answer = " ".join(
            block.text
            for block in response.content
                if hasattr(block, "text")
        ).strip()

    else:
        final_answer = str(response.content).strip()

    print("SYNTHESIS FINISH REASON:",
      metadata.get("finish_reason"))

    return final_answer



def research_agent(state: AgentState) -> AgentState:
    print("\n========== RESEARCH AGENT ENTERED ==========")
    start = time.time()
    query = state.get("user_query")
    active_agent = "research_agent"

    if not validate_query(query):

        add_error(state, "Missing research query")

        return set_state(
        state=state,
        status="failed",
        confidence=LOW_CONFIDENCE,
        agent=active_agent,
        trace_action=RESEARCH_FAILED,
        extra={
            "workflow_step": RESEARCH_FAILED
            }
        )

    try:
        add_trace(state, active_agent, QUERY_OPTIMIZATION_STARTED)
        #llm = gemini_llm_client(
        #model=GEMINI_MODEL,
        #temperature=0,
        #max_tokens=2048
        #)
        synthesis_llm = gemini_llm_client(
        model=GEMINI_MODEL,
        temperature=0.2,
        max_tokens=4096
        )

        optimizer_llm = gemini_llm_client(
        model=GEMINI_MODEL,
        temperature=0,
        max_tokens=300
        )   
     
        # =========================
        # QUERY OPTIMIZATION
        # =========================

        query_modified = optimize_search_query(
            query=query,
            llm=optimizer_llm,
            state=state
        )
        print("\n========== OPTIMIZED SEARCH QUERIES ==========")

        for i, search_query in enumerate(query_modified, 1):
            print(f"{i}. {search_query}")

        print("==============================================\n")


      
        add_trace(state, active_agent, QUERY_OPTIMIZATION_COMPLETED)
        # =========================
        # RETRIEVAL
        # =========================

        #search_results = tavily_search(
        #    query=query_modified
        #)
        print("BEFORE RETRIEVAL")
        print("query_modified type:", type(query_modified))
        print("query_modified value:", query_modified)

        all_results = []

        print("BEFORE LOOP")

        for search_query in query_modified:
            print("INSIDE LOOP")            
            print(f"\n========== WEB SEARCH ==========")
            print(f"Query: {search_query}")
            print("================================\n")

            result = invoke_tool_with_trace(
            state=state,
            tool=web_search_tool,
            tool_input={"query": search_query},
            agent=active_agent,
            operation="web_search",
            )

            print("\n========== WEB SEARCH RESULT ==========")
            print(type(result))
            print(result)
            print("=======================================\n")

            all_results.extend(
            result.get("results", [])
            )

        search_results = {
            "results": all_results
            }

        

        add_trace(state, active_agent, RETRIEVAL_COMPLETED)

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
                confidence=LOW_CONFIDENCE,
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
            llm=synthesis_llm,
            state=state
            )
        
        add_trace(state, active_agent, SYNTHESIS_COMPLETED)
        
        add_trace(
        state,
        agent=active_agent,
        action=RESEARCH_COMPLETED
        )

        results = search_results.get("results", [])
        source_count = len(results)

        return set_state(
            state=state,
            start=start,
            confidence=max(0.5,min(source_count / 5, 1.0)),
            status="success",
            agent=active_agent,
            trace_action=RESEARCH_COMPLETED,
            extra={
                "optimized_query": query_modified,
                "research_data": search_results,
                "research_content": synthesized_answer,
                "source_count": source_count,
                "workflow_step": RESEARCH_COMPLETED,
            }
        )

    except Exception as e:

        print("\n========== RESEARCH AGENT ERROR ==========")
        print(repr(e))
        import traceback
        traceback.print_exc()
        print("==========================================\n")

   

        add_error(state, str(e))
        execution_time = round(time.time() - start, 2)
        return set_state(
            state=state,
            start=start,
            confidence=LOW_CONFIDENCE,
            status="failed",
            agent=active_agent,
            trace_action=RESEARCH_FAILED,
            extra={
                "workflow_step": RESEARCH_FAILED,
                "execution_time": execution_time
            }
        )
