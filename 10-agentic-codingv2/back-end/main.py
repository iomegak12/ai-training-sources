"""
Agentic RAG - Main Entry Point

This module provides the main interface for the Agentic RAG system.
It includes functions for both direct and streaming responses.
"""

from typing import Dict, Generator, Any
from langchain_core.messages import HumanMessage
from agents import create_agent


def query_agent_direct(question: str) -> Dict[str, Any]:
    """
    Query the agent and get a direct response.
    
    This function creates an agent, sends a question, and returns
    the complete response in one go.
    
    Args:
        question: The question or prompt to send to the agent
        
    Returns:
        Dictionary containing the agent's response and metadata
        
    Example:
        >>> response = query_agent_direct("Tell me about LangSmith")
        >>> print(response)
    """
    # Create the agent
    agent = create_agent()
    
    # Invoke the agent with the question
    output = agent.invoke({
        "messages": [
            HumanMessage(content=question)
        ]
    })
    
    return output


def query_agent_streaming(question: str) -> Generator[Dict[str, Any], None, None]:
    """
    Query the agent and get a streaming response.
    
    This function creates an agent, sends a question, and yields
    response chunks as they are generated.
    
    Args:
        question: The question or prompt to send to the agent
        
    Yields:
        Dictionary chunks containing parts of the agent's response
        
    Example:
        >>> for chunk in query_agent_streaming("Tell me about LangSmith"):
        ...     print(chunk)
        ...     print("***********")
    """
    # Create the agent
    agent = create_agent()
    
    # Stream the agent's response
    for stream_chunk in agent.stream({
        "messages": [
            HumanMessage(content=question)
        ]
    }):
        yield stream_chunk


def main():
    """
    Main function demonstrating usage of the Agentic RAG system.
    
    This function shows examples of both direct and streaming queries.
    """
    print("=" * 80)
    print("Agentic RAG System")
    print("=" * 80)
    print()
    
    # Example 1: Direct Response
    print("Example 1: Direct Response")
    print("-" * 80)
    question1 = "Tell me about LangSmith"
    print(f"Question: {question1}")
    print()
    
    response = query_agent_direct(question1)
    print("Response:")
    print(response)
    print()
    
    # Example 2: Streaming Response
    print("=" * 80)
    print("Example 2: Streaming Response")
    print("-" * 80)
    question2 = "What is the Indian Constitution?"
    print(f"Question: {question2}")
    print()
    print("Streaming Response:")
    
    for chunk in query_agent_streaming(question2):
        print(chunk)
        print("***********")
    
    print()
    print("=" * 80)
    print("Done!")
    print("=" * 80)


if __name__ == "__main__":
    main()
