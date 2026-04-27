from langchain.agents import initialize_agent, AgentType
from utils.llm import get_llm
from tools.agent_tools import market_tool, risk_tool, news_tool, rag_tool

llm = get_llm()

tools = [market_tool, risk_tool, news_tool, rag_tool]

advisor_llm = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)