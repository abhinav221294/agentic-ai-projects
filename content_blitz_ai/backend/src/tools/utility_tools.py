# =========================
# utility_tools.py
# =========================

from datetime import datetime

from langchain.tools import tool


@tool
def current_timestamp_tool():

    """
    Returns current timestamp.
    """

    return str(datetime.now())


@tool
def word_count_tool(
    text: str
):

    """
    Returns total word count.
    """

    return len(text.split())