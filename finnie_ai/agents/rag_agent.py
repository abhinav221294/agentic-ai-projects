from tools.rag_pipeline import RAGPipeline
from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import RAG_PROMPT
import time
from utils.rag_loader import rag

def relevance_boost(r, query):
    content = r.get("content", "").lower()
    overlap = sum(1 for word in query.split() if word in content)
    return r.get("score", 1.0) - (0.005 * overlap)


# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
def _set(state, start, answer, confidence, source, extra=None):
    state["answer"] = answer
    state["agent"] = "rag_agent"
    state["confidence"] = confidence
    state["source"] = source
    state["decision_source"] = "tool"
    state["answer_source"] = "rag"
    state["execution_time"] = round(time.time() - start, 2)

    if extra:
        state.update(extra)

    return state


def rag_agent(state: AgentState) -> AgentState:
    start = time.time()

    tools = state.setdefault("tools_used", [])
    if "rag_pipeline" not in tools:
        tools.append("rag_pipeline")

    # -------------------------
    # QUERY
    # -------------------------
    raw_query = state["query"]
    query = raw_query.lower()

    # -------------------------
    # RETRIEVE
    # -------------------------
    results = rag.retrieve(query=query)

    # -------------------------
    # NO RESULTS
    # -------------------------
    if not results:
        return _set(
            state, start,
            "I couldn't find strong information in the documents. You can try rephrasing your question or ask something more specific.",
            0.5,
            []
        )

    # -------------------------
    # DEDUPLICATE
    # -------------------------
    seen_content = set()
    unique_results = []

    for r in results:
        content = r.get("content", "").strip()
        key = content[:200]
        if key not in seen_content:
            seen_content.add(key)
            unique_results.append(r)

    # -------------------------
    # SORT
    # -------------------------
    unique_results = sorted(unique_results, key=lambda x: relevance_boost(x, query))

    # -------------------------
    # FILTER
    # -------------------------
    scores = [r.get("score", 1.0) for r in unique_results]

    if scores:
        dynamic_threshold = min(scores) + 0.2
    else:
        dynamic_threshold = 0.5

    filtered_results = [r for r in unique_results if r.get("score", 1.0) <= dynamic_threshold]

    if not filtered_results:
        filtered_results = unique_results[:1]

    # -------------------------
    # CONTEXT
    # -------------------------
    context = "\n\n".join([r.get("content", "") for r in filtered_results])

    if len(context.strip()) < 50:
        return _set(
            state, start,
            "I couldn't find strong information in the documents. You can try rephrasing your question or ask something more specific.",
            0.5,
            []
        )

    # -------------------------
    # MEMORY
    # -------------------------
    memory = state.get("memory", [])

    conversation = ""
    for m in memory[-3:]:
        conversation += f"\nUser: {m.get('user', '')}\nAssistant: {m.get('assistant', '')}\n"

    # -------------------------
    # LLM GENERATION
    # -------------------------
    llm = get_llm(temperature=0.3, max_tokens=1000)

    final_prompt = f"""{RAG_PROMPT}

IMPORTANT:
- Use context as primary source
- If context is weak or incomplete, use general knowledge to help
- If this is a follow-up question, continue from previous answer
- Do NOT say "no information found" if you can reasonably answer

This may be a follow-up question. Use previous conversation to infer meaning.

Conversation:
{conversation}

Question:
{query}

Context:
{context}
"""

    try:
        response = llm.invoke(final_prompt)
        answer = response.content

        show_source = "couldn't find relevant information" not in answer.lower()

    except Exception:
        answer = "Here’s what I found:\n\n" + context[:1000]
        show_source = False

    # -------------------------
    # SOURCES
    # -------------------------
    combined_sources = list(set([r.get("source_file_name", "unknown") for r in filtered_results]))

    if show_source:
        answer += "\n\n📚 Based on internal documents."

    return _set(
        state, start,
        answer,
        0.9 if show_source else 0.5,
        combined_sources if show_source else []
    )