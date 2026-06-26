from src.agents.research_agent import research_agent
from src.agents.strategist_agent import strategist_agent
from src.agents.blog_writer_agent import blog_writer_agent


def blog_workflow(state):

    state = research_agent(state)

    if state["status"] == "failed":
        return state

    state = strategist_agent(state)

    if state["status"] == "failed":
        return state

    state = blog_writer_agent(state)

    return state