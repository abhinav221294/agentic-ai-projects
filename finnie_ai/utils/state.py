from typing import TypedDict, Optional, Dict, List, Union, Literal

class AgentState(TypedDict, total=False):
    query: str
    category: str
    answer: str
    agent: str            
    confidence: float
    memory: List[Dict]  
    clarification_needed: bool
    next_question: str
    profile: Dict[str, Optional[str]]
    trace: List[Union[str, Dict]]
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
    "execution"]]
    selected_funds: List[str]
    expected_next_input: float