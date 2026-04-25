from langgraph.graph import StateGraph, END

from utils.state import AgentState
from agents.rag_agent import rag_agent
from agents.router_agent import router_agent
from agents.risk_agent import risk_agent
from agents.advisor_agent import advisor_agent
from agents.market_agent import market_agent
from agents.news_agent import news_agent
from utils.llm import get_llm

def fallback_agent(state: AgentState) -> AgentState:
    query = state.get("query", "").lower()

    llm = get_llm(temperature=0.2)

    response = llm.invoke(f"""User asked: "{query}"

You're a finance-focused assistant having a casual chat. The user asked about something outside your scope.

Respond in 2–3 lines:
1. Name the actual topic from the query, then make a brief neutral observation about it
2. Say you usually stick to finance
3. Name what you cover in passing — like mentioning it, not offering it


                          
RULES:
- Use the actual topic the user asked about — do not substitute or paraphrase it
- No explaining the off-topic subject
- No questions
- No filler affirmations or compliments ("great way to...", "Interesting!", "Sounds fun!")
- No availability offers ("happy to", "feel free", "let me know", "I'm here for")
- Don't start with "I"
- Last line names your scope — it doesn't invite or offer
               
Use variation at starting:
"Topic, huh?"
"Oh, Topic?"
"Ah, Topic"
                          
Replace:
“well-loved” ❌
“fascinating” ❌
“intriguing” ❌

With:
“popular” ✅
                          
TONE: Like a person casually saying "not really my thing, I'm more into X"

TARGET OUTPUT (match this style, don't copy it):
"Cricket? That's a popular sport. I usually stick to finance though — things like investing and markets."

BANNED WORDS/PHRASES:
- "sounds interesting / intriguing"
- "my focus is on"
- "I specialize in"
- "happy to" / "feel free" / "let me know"
- Any compliment about the off-topic subject
CRITICAL STYLE:
- Keep sentences simple and spoken (not written/formal)
- Avoid structured or formal phrasing
- Should sound like casual speech, not a statement

EXAMPLE:
Topic? That's a popular sport.  
I usually stick to finance though—stuff like stocks and budgeting.""")
    
    if not response or not response.content:
        state["answer"] = "I usually focus on finance—things like investing and markets."
    else:
        state["answer"] = response.content.strip()
    state["agent"] = "fallback_agent"
    return state


def __build_workflow():
    """
    Builds and compiles a LangGraph workflow for a multi-agent system.

    Flow:
    1. Start with router_agent (entry point)
    2. Router decides category based on query
    3. Conditional routing sends state to appropriate agent
    4. Selected agent processes query and updates state
    5. Workflow terminates at END

    Returns:
        Compiled LangGraph workflow (ready to invoke)
    """

    # ---------------------------------------------------
    # Step 1: Initialize workflow with state schema
    # ---------------------------------------------------
    # AgentState defines structure of shared data:
    # {
    #   "query": str,
    #   "category": str,
    #   "answer": str
    # }
    workflow = StateGraph(AgentState)

    # ---------------------------------------------------
    # Step 2: Register all agents (nodes)
    # ---------------------------------------------------
    # Each node represents a function that:
    # - takes state as input
    # - modifies it
    # - returns updated state

    workflow.add_node("router_agent", router_agent)     # decides route
    workflow.add_node("rag_agent", rag_agent)           # general Q&A
    workflow.add_node("market_agent", market_agent)     # stock/price queries
    workflow.add_node("risk_agent", risk_agent)         # risk-related queries
    workflow.add_node("advisor_agent", advisor_agent)   # investment advice
    workflow.add_node("news_agent", news_agent) 
    workflow.add_node("fallback_agent", fallback_agent)
    # ---------------------------------------------------
    # Step 3: Define entry point
    # ---------------------------------------------------
    # Workflow always starts with router_agent
    workflow.set_entry_point("router_agent")

    # ---------------------------------------------------
    # Step 4: Define valid categories
    # ---------------------------------------------------
    # This acts as a safeguard to avoid invalid routing
    VALID_CATEGORIES = {"rag", "market", "risk", "advisor","news","none"}

    # ---------------------------------------------------
    # Step 5: Routing decision function
    # ---------------------------------------------------
    # This function reads state["category"] (set by router_agent)
    # and determines which node to execute next

    def __route_decision(state: AgentState):
        category = state.get("category", "none")

        # ✅ Ensure string only
        if not isinstance(category, str):
            print("[Routing Error] Invalid category:", category)
            return "none"

        if category == "none":
            return "none"

        return category if category in VALID_CATEGORIES else "none"

        ## ✅ Handle "none" BEFORE routing
        #if category == "none":
        #    state["answer"] = "I can only help with finance-related questions."
        #    return "end"   # 👈 stops execution
    
    # ---------------------------------------------------
    # Step 6: Add conditional edges
    # ---------------------------------------------------
    # Based on output of route_decision:
    # - "rag"     → rag_agent
    # - "market"  → market_agent
    # - "risk"    → risk_agent
    # - "advisor" → advisor_agent

    workflow.add_conditional_edges(
        "router_agent",       # source node
        __route_decision,       # decision function
        {
            "rag": "rag_agent",
            "market": "market_agent",
            "risk": "risk_agent",
            "advisor": "advisor_agent",
            "news": "news_agent",
            "none": "fallback_agent"
        }
    )

    # ---------------------------------------------------
    # Step 7: Define termination (END)
    # ---------------------------------------------------
    # After each agent finishes execution, workflow ends

    workflow.add_edge("rag_agent", END)
    workflow.add_edge("market_agent", END)
    workflow.add_edge("risk_agent", END)
    workflow.add_edge("advisor_agent", END)
    workflow.add_edge("news_agent", END)
    workflow.add_edge("fallback_agent", END)

    # ---------------------------------------------------
    # Step 8: Compile workflow
    # ---------------------------------------------------
    # Converts graph definition into executable object

    return workflow.compile()

app = __build_workflow()

def run_workflow(state: dict):
    #return app.invoke(state)
    result = app.invoke(state)
    if not result:
        return {"answer": "Something went wrong.", "agent": "system"}
    return result