"""Agentic RAG agent implementation."""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config.settings import settings
from tools import (
    create_google_search_tool,
    create_wikipedia_tool,
    create_arxiv_tool,
    create_retriever_tool
)


def create_agent():
    """
    Create and configure the Agentic RAG agent.
    
    This function initializes the LLM, creates all necessary tools,
    and returns a configured React agent.
    
    Returns:
        Configured React agent executor
    """
    # Validate settings
    settings.validate()
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    # Create all tools
    google_search = create_google_search_tool()
    wikipedia = create_wikipedia_tool()
    arxiv = create_arxiv_tool()
    retriever = create_retriever_tool()
    
    # Combine all tools
    tools = [arxiv, google_search, wikipedia, retriever]
    
    # Create the React agent
    agent_executor = create_react_agent(
        llm,
        tools=tools
    )
    
    return agent_executor
