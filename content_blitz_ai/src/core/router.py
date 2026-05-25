from src.agents.blog_writer_agent import blog_writer_agent
from src.agents.linkedin_writer_agent import linkedin_writer_agent
from src.agents.research_agent import research_agent
from src.agents.fallback_agent import fallback_agent


def route_workflow(state):

    category = state.get("current_intent")

    if category == "blog":
        return blog_writer_agent(state)

    elif category == "linkedin":
        return linkedin_writer_agent(state)

    elif category == "research":
        return research_agent(state)

    elif category == "image":
        return fallback_agent(state)

    elif category == "strategy":
        return fallback_agent(state)

    else:
        return fallback_agent(state)