"""Wikipedia search tool."""

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from config.settings import settings


def create_wikipedia_tool():
    """
    Create and return the Wikipedia search tool.
    
    Returns:
        WikipediaQueryRun tool configured with settings
    """
    api_wrapper = WikipediaAPIWrapper(
        top_k_results=settings.WIKIPEDIA_TOP_K,
        doc_content_chars_max=settings.WIKIPEDIA_DOC_CONTENT_MAX_CHARS
    )
    
    wiki = WikipediaQueryRun(
        name="WikipediaSearch",
        description="Use this tool when you want to analyze for information on Wikipedia by Terms, Keywords or any Topics.",
        api_wrapper=api_wrapper
    )
    
    return wiki
