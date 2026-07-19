# =========================
# content_tools.py
# =========================

from langchain.tools import tool


@tool
def blog_outline_tool(
    topic: str
):

    """
    Generates blog outline structure.
    """

    return f"Generated blog outline for: {topic}"


@tool
def linkedin_hook_tool(
    topic: str
):

    """
    Generates engaging LinkedIn hook.
    """

    return f"Generated LinkedIn hook for: {topic}"


@tool
def generate_cta_tool(
    content_type: str
):
    """
    Generates call-to-action based on content type.
    """

    return f"Generated CTA for {content_type}"

@tool
def generate_title_tool(
    topic: str
):

    """
    Generates content title from topic.
    """

    return f"Generated title for: {topic}"
