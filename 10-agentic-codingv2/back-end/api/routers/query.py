"""Query endpoint for AI agent."""

from fastapi import APIRouter, HTTPException, Depends, status
from langchain_core.messages import HumanMessage
from api.models import QueryRequest, QueryResponse, ErrorResponse
from api.dependencies import get_agent
from typing import List
import logging

router = APIRouter(tags=["Query"])
logger = logging.getLogger(__name__)


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query the AI Agent",
    description="Send a question to the AI agent and receive an answer",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """
    Query the AI agent with a question.
    
    The agent will automatically select and use appropriate tools based on the question:
    - Google Search: For real-time information
    - Wikipedia: For general knowledge
    - ArXiv: For academic papers
    - LangSmith Retriever: For LangSmith documentation
    
    Args:
        request: QueryRequest containing the question and optional parameters
        
    Returns:
        QueryResponse: The agent's answer along with metadata
        
    Raises:
        HTTPException: If the query fails
    """
    try:
        agent = get_agent()
        
        # Invoke the agent
        logger.info(f"Processing query: {request.question[:100]}...")
        
        result = agent.invoke({
            "messages": [HumanMessage(content=request.question)]
        })
        
        # Extract the answer from the result
        answer = ""
        tools_used = []
        
        if "messages" in result:
            # Get the last message which should be the final answer
            messages = result["messages"]
            if messages:
                last_message = messages[-1]
                answer = getattr(last_message, "content", str(last_message))
            
            # Extract tools used from intermediate messages
            for msg in messages:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        if tool_name not in tools_used:
                            tools_used.append(tool_name)
        else:
            # Fallback: convert entire result to string
            answer = str(result)
        
        logger.info(f"Query processed successfully. Tools used: {tools_used}")
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            tools_used=tools_used
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )
