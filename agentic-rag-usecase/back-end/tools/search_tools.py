"""
Search Tools for Agentic RAG API
Provides Wikipedia, ArXiv, and DuckDuckGo search capabilities
"""
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_core.tools import tool
from config.logging_config import get_logger

logger = get_logger(__name__)


def get_wikipedia_tool() -> WikipediaQueryRun:
    """
    Create and return Wikipedia search tool
    
    Returns:
        WikipediaQueryRun tool configured for topic searches
    """
    try:
        api_wrapper = WikipediaAPIWrapper(
            top_k_results=1, 
            doc_content_chars_max=1000
        )
        
        wiki = WikipediaQueryRun(
            name="WikipediaSearch",
            description="Use this tool when you want to search for information on Wikipedia by Terms, Keywords or any Topics.",
            api_wrapper=api_wrapper
        )
        
        logger.info("✓ Wikipedia search tool initialized")
        return wiki
        
    except Exception as e:
        logger.error(f"Error initializing Wikipedia tool: {str(e)}", exc_info=True)
        raise


def get_arxiv_tool() -> ArxivQueryRun:
    """
    Create and return ArXiv search tool for academic papers
    
    Returns:
        ArxivQueryRun tool configured for paper searches
    """
    try:
        arxiv_wrapper = ArxivAPIWrapper(
            top_k_results=1, 
            doc_content_chars_max=1000
        )
        
        arxiv = ArxivQueryRun(
            name="ArxivSearch",
            description="Use this tool to search for academic papers and research articles on ArXiv. Useful for scientific and technical topics.",
            api_wrapper=arxiv_wrapper
        )
        
        logger.info("✓ ArXiv search tool initialized")
        return arxiv
        
    except Exception as e:
        logger.error(f"Error initializing ArXiv tool: {str(e)}", exc_info=True)
        raise


@tool("DuckDuckGoSearch")
def duckduckgo_search(query_string: str) -> str:
    """
    Search the internet using DuckDuckGo for any kinds of information.
    
    Use this tool when:
    - You need to search the internet for current information
    - Looking for general web content and facts
    - Prefer this for long queries
    - Should NOT be used for Article search or Topic Search (use Wikipedia/ArXiv instead)
    
    Args:
        query_string: The search query string
        
    Returns:
        Search results from DuckDuckGo
    """
    try:
        search = DuckDuckGoSearchAPIWrapper()
        return search.run(query_string)
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {str(e)}", exc_info=True)
        return f"Error performing search: {str(e)}"


def get_duckduckgo_tool():
    """
    Get DuckDuckGo search tool
    
    Returns:
        DuckDuckGo search tool
    """
    logger.info("✓ DuckDuckGo search tool initialized")
    return duckduckgo_search


def get_all_search_tools() -> list:
    """
    Get all search tools (Wikipedia, ArXiv, DuckDuckGo)
    
    Returns:
        List of all search tools
    """
    try:
        tools = [
            get_arxiv_tool(),
            get_duckduckgo_tool(),
            get_wikipedia_tool()
        ]
        
        logger.info(f"✓ Loaded {len(tools)} search tools")
        return tools
        
    except Exception as e:
        logger.error(f"Error loading search tools: {str(e)}", exc_info=True)
        raise
