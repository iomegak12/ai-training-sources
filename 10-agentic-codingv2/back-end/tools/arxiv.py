"""ArXiv research paper search tool."""

from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun
from config.settings import settings


def create_arxiv_tool():
    """
    Create and return the ArXiv search tool.
    
    Returns:
        ArxivQueryRun tool configured with settings
    """
    arxiv_wrapper = ArxivAPIWrapper(
        top_k_results=settings.ARXIV_TOP_K,
        doc_content_chars_max=settings.ARXIV_DOC_CONTENT_MAX_CHARS
    )
    
    arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)
    
    return arxiv
