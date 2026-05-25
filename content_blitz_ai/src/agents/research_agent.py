from src.workflows.state_management import AgentState,set_state
from src.prompts.prompt import RESEARCH_PROMPT, RESEARCH_SYNTHESIS_PROMPT
#from src.integrations.perplexity_client import perplexity_search
from src.integrations.tavily_client import tavily_search
from src.integrations.gemini_client import gemini_llm_client
import time
from dotenv import load_dotenv

load_dotenv()

def optimize_search_query(query, llm):

    prompt = f"""
Convert the user request into an optimized web search query.

Rules:
- concise
- keyword rich
- no explanations
- optimized for web retrieval

User Query:
{query}
"""

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
            f"""`   `Title:
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

    query = state["user_query"]

    active_agent = "researcher"

    llm = gemini_llm_client()

    try:
        # =========================
        # QUERY OPTIMIZATION
        # =========================

        query_modified = optimize_search_query(
            query=query,
            llm=llm
        )

         # =========================
        # RETRIEVAL
        # =========================

        search_results = tavily_search(
            query=query_modified
        )

         # =========================
        # FORMAT RESULTS
        # =========================

        formatted_results = format_search_results(
            search_results
        )

        # =========================
        # SYNTHESIS
        # =========================

        synthesized_answer = synthesize_research(
            user_query=query,
            formatted_results=formatted_results,
            llm=llm
            )

        return set_state(
            state=state,
            start=start,
            confidence=0.9,
            status="success",
            agent=active_agent,
            trace_action="research_completed",
            extra={
                "optimized_query": query_modified,
                "research_data": search_results,
                "workflow_step": "research_completed"
            },
            answer=synthesized_answer
        )

    except Exception as e:

        state["errors"].append(str(e))

        return set_state(
            state=state,
            start=start,
            confidence=0.2,
            status="failed",
            agent=active_agent,
            trace_action="research_failed",
            extra={
                "workflow_step": "research_failed"
            }
        )
