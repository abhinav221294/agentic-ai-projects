from tools.rag_pipeline import RAGPipeline
from utils.state import AgentState
from utils.llm import get_llm
from utils.prompts import RAG_PROMPT

# Initialize the RAG pipeline
rag = RAGPipeline()

def relevance_boost(r, query):
    content = r.get("content", "").lower()
    overlap = sum(1 for word in query.split() if word in content)
    return r.get("score", 1.0) - (0.01 * overlap)

def rag_agent(state: AgentState) -> AgentState:
    """
    RAG Agent (Improved)

    - Retrieves relevant chunks
    - Deduplicates
    - Ranks by relevance
    - Filters weak results
    - Returns clean answer
    """

    # ---------------------------------------------------
    # Step 1: Extract query
    # ---------------------------------------------------
    raw_query = state["query"]
    query = raw_query.lower()

    # ---------------------------------------------------
    # Step 2: Retrieve results
    # ---------------------------------------------------
    results = rag.retrieve(query=query)

    # ---------------------------------------------------
    # Step 3: Handle no results
    # ---------------------------------------------------
    if not results:
        state["answer"] = "I couldn't find strong information in the documents.You can try rephrasing your question or ask something more specific."
        state["agent"] = "rag_agent"
        state["source"] = []
        return state

    # ---------------------------------------------------
    # Step 4: Remove duplicate content
    # ---------------------------------------------------
    seen_content = set()
    unique_results = []
    
    for r in results:
        content = r.get("content", "")
        if content not in seen_content:
            seen_content.add(content)
            unique_results.append(r)

    # ---------------------------------------------------
    # Step 5: Sort by relevance (lower score = better)
    # ---------------------------------------------------
    unique_results = sorted(unique_results, key=lambda x: relevance_boost(x, query))

    # ---------------------------------------------------
    # Step 6: Filter weak results
    # ---------------------------------------------------
    #threshold = 0.5
    #filtered_results = [r for r in unique_results if r.get("score", 1.0) < threshold]
    scores = [r.get("score", 1.0) for r in unique_results]

    if scores:
        dynamic_threshold = min(scores) + 0.2
    else:
        dynamic_threshold = 0.5

    filtered_results = [r for r in unique_results if r.get("score", 1.0) <= dynamic_threshold]

    # fallback if everything filtered out
    if not filtered_results:
        filtered_results = unique_results[:1]

    # ---------------------------------------------------
    # Step 7: Prepare context
    # ---------------------------------------------------
    context = "\n\n".join([r.get("content", "") for r in filtered_results])
    

    if len(context.strip()) < 50:
        state["answer"] = "I couldn't find strong information in the documents.You can try rephrasing your question or ask something more specific."
        state["agent"] = "rag_agent"
        state["source"] = []
        state["confidence"] = "HIGH"

        return state

    # ---------------------------------------------------
    # Step 8: Generate answer using LLM
    # ---------------------------------------------------
    memory = state.get("memory", [])

    conversation = ""
    for m in memory[-3:]:
        conversation += f"\nUser: {m.get('user', '')}\nAssistant: {m.get('assistant', '')}\n"

    llm = get_llm()

    final_prompt = f"""{RAG_PROMPT}
IMPORTANT:
- Answer MUST be based on the provided context
- Do NOT use outside knowledge if context is available
- If context is insufficient, say so clearly

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
        
        if "couldn't find relevant information" in answer.lower():
            show_source = False
        else:
            show_source = True

    except Exception:
        # fallback → return raw context (safe)
        answer = "Here’s what I found:\n\n" + context[:1000]
        show_source = False
    # ---------------------------------------------------
    # Step 9: Extract sources
    # ---------------------------------------------------
    combined_sources = list(set([r.get("source_file_name", "unknown") for r in filtered_results]))

    # ---------------------------------------------------
    # Step 10: Update state
    # ---------------------------------------------------

    if show_source:
        answer += "\n\n📚 Based on internal documents."

    state["answer"] = answer
    state["agent"] = "rag_agent"
    state["source"] = combined_sources if show_source else []
    state["confidence"] = "HIGH"  if show_source else "LOW"

    return state