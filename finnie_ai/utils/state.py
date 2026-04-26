from typing import TypedDict, Optional, Dict, List

class AgentState(TypedDict, total=False):
    query: str
    category: str
    answer: str
    agent: str          
    source: List[str]   
    confidence: str
    memory: List[Dict]  
    clarification_needed: bool
    next_question: str
    profile: Dict[str, Optional[str]]             