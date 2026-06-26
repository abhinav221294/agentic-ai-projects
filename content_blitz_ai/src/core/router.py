
from src.agents.research_agent import research_agent
from src.agents.fallback_agent import fallback_agent
from src.agents.image_agent import image_agent
from src.workflows.blog_workflow import blog_workflow
from src.workflows.linkedin_workflow import linkedin_workflow

def route_workflow(state):

    category = state.get("current_intent")

    if category == "blog":
        return blog_workflow(state)

    elif category == "linkedin":
        return linkedin_workflow(state)

    elif category == "research":
        return research_agent(state)

    elif category == "image":
        return image_agent(state)

    return fallback_agent(state)