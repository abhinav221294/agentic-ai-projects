from typing import TypedDict, Optional, List, Dict, Literal

class MemoryItem(TypedDict, total=False):
    query: str
    assistant: str
    stage: str
    agent: str

class AgentState(TypedDict, total=False):
    query: str
    category: str
    answer: str
    agent: str            
    confidence: float
    memory: List[MemoryItem] 
    #clarification_needed: bool
    #next_question: str
    profile: Dict[str, Optional[str]]
    trace: List[Dict]
    tools_used: List[str]
    execution_time: float
    error: Optional[str]
    answer_source: str
    query_type: str
    decision_source: str
    stage: Optional[Literal[
        "collect_profile",
        "advice",
        "suggestion",
        "execution"
    ]]
    selected_funds: List[str]
    expected_next_input: Optional[str]
    thread_id: Optional[str]
    advisor_insights: Optional[str]
    advisor_allocation: Optional[Dict[str, int]]
    advisor_advice: Optional[str]

    market_context: Optional[str]
    news_context: Optional[str]

    last_intent: Optional[str]
    active_asset: Optional[str]