"""Google Search tool using Serper API."""

from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper


@tool("GoogleSearch")
def google_search(query_string: str) -> str:
    """
    Search the internet for information using Google Search.
    
    Useful to search for any kinds of information and
    when you need to search the internet for any kinds of information, use this tool.
    Prefer this tool when you search for long queries.
    Should not be used for Article search or Topic Search.
    You should use this only when you need to get real-time information about a topic.
    
    Args:
        query_string: The search query string
        
    Returns:
        Search results as a string
    """
    search = GoogleSerperAPIWrapper()
    return search.run(query_string)


def create_google_search_tool():
    """Create and return the Google Search tool."""
    return google_search
