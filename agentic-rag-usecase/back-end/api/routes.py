"""
API Routes
FastAPI endpoint handlers for /chat, /chat-stream, /health, /tools
"""
import time
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import AsyncIterator
from api.models import (
    ChatRequest, ChatResponse, StreamEvent, StreamEventType,
    HealthResponse, HealthStatus, ComponentHealth,
    ToolsResponse, ToolInfo, ConversationMessage, MessageRole,
    ErrorResponse
)
from api.dependencies import AgentServiceDep, FAISSServiceDep, CustomerManagerDep
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with Agent (Blocking)",
    description="""
    Send a message to the agentic RAG system and receive a complete response.
    
    This is a blocking endpoint that returns the full response after the agent
    completes its reasoning and tool use. Use `/chat-stream` for streaming responses.
    
    The agent has access to multiple tools:
    - Wikipedia, ArXiv, DuckDuckGo for search
    - CRM database (business client queries)
    - Chinook SQL database (music store analytics)
    - FAISS vector store (LangSmith documentation)
    """,
    responses={
        200: {"model": ChatResponse, "description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def chat(
    request: ChatRequest,
    agent: AgentServiceDep
) -> ChatResponse:
    """
    Chat with the agentic RAG system (blocking)
    
    Args:
        request: Chat request with message and optional conversation history
        agent: Agent service dependency
        
    Returns:
        ChatResponse with assistant's message and updated conversation history
    """
    try:
        start_time = time.time()
        logger.info(f"Chat request received: {request.message[:100]}...")
        
        # Convert conversation history to dict format
        history = None
        if request.conversation_history:
            history = [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Invoke agent
        result = agent.invoke(
            message=request.message,
            conversation_history=history
        )
        
        # Extract response from agent result
        # The agent executor returns {"messages": [...]}
        messages = result.get("messages", [])
        
        # Build conversation history
        conversation_history = []
        assistant_message = ""
        
        for msg in messages:
            msg_type = msg.__class__.__name__
            content = msg.content if hasattr(msg, 'content') else str(msg)
            
            if msg_type == "HumanMessage":
                conversation_history.append(
                    ConversationMessage(role=MessageRole.USER, content=content)
                )
            elif msg_type == "AIMessage":
                conversation_history.append(
                    ConversationMessage(role=MessageRole.ASSISTANT, content=content)
                )
                assistant_message = content  # Last AI message is the response
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"Chat response generated in {response_time_ms}ms")
        
        return ChatResponse(
            message=assistant_message,
            conversation_history=conversation_history,
            metadata={
                "response_time_ms": response_time_ms,
                "tools_available": len(agent.tools)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post(
    "/chat-stream",
    summary="Chat with Agent (Streaming)",
    description="""
    Send a message to the agentic RAG system and receive streaming responses.
    
    This endpoint streams Server-Sent Events (SSE) as the agent reasons and uses tools.
    Each event contains information about agent steps, tool calls, and intermediate results.
    
    Event types:
    - `start`: Streaming started
    - `agent`: Agent reasoning step
    - `tool`: Tool execution result
    - `end`: Streaming complete
    - `error`: Error occurred
    """,
    responses={
        200: {"description": "Server-Sent Events stream"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def chat_stream(
    request: ChatRequest,
    agent: AgentServiceDep
) -> StreamingResponse:
    """
    Chat with the agentic RAG system (streaming)
    
    Args:
        request: Chat request with message and optional conversation history
        agent: Agent service dependency
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    logger.info(f"Chat stream request received: {request.message[:100]}...")
    
    async def event_generator() -> AsyncIterator[str]:
        """Generate Server-Sent Events"""
        try:
            # Send start event
            start_event = StreamEvent(
                event=StreamEventType.START,
                data={"message": "Streaming started"}
            )
            yield f"data: {start_event.model_dump_json()}\n\n"
            
            # Convert conversation history to dict format
            history = None
            if request.conversation_history:
                history = [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in request.conversation_history
                ]
            
            # Stream agent responses
            async for chunk in agent.stream(
                message=request.message,
                conversation_history=history
            ):
                # Determine event type based on chunk keys
                if "agent" in chunk:
                    event_type = StreamEventType.AGENT
                elif "tools" in chunk:
                    event_type = StreamEventType.TOOL
                else:
                    event_type = StreamEventType.AGENT
                
                # Create stream event
                stream_event = StreamEvent(
                    event=event_type,
                    data=chunk
                )
                
                yield f"data: {stream_event.model_dump_json()}\n\n"
            
            # Send end event
            end_event = StreamEvent(
                event=StreamEventType.END,
                data={"message": "Streaming complete"}
            )
            yield f"data: {end_event.model_dump_json()}\n\n"
            
        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}", exc_info=True)
            error_event = StreamEvent(
                event=StreamEventType.ERROR,
                data={"error": str(e)}
            )
            yield f"data: {error_event.model_dump_json()}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="""
    Check the health status of the API and its components.
    
    Returns health information for:
    - Agent service
    - FAISS vector store
    - Database connections
    - Overall system status
    """,
    responses={
        200: {"model": HealthResponse, "description": "Health status"}
    }
)
async def health(
    agent: AgentServiceDep,
    faiss: FAISSServiceDep,
    customer_db: CustomerManagerDep
) -> HealthResponse:
    """
    Perform health check on all components
    
    Args:
        agent: Agent service dependency
        faiss: FAISS service dependency
        customer_db: Customer database dependency
        
    Returns:
        HealthResponse with component statuses
    """
    components = {}
    overall_status = HealthStatus.HEALTHY
    
    # Check agent service
    try:
        agent_ready = agent.is_ready()
        if agent_ready:
            agent_info = agent.get_info()
            components["agent"] = ComponentHealth(
                status=HealthStatus.HEALTHY,
                message="Agent service operational",
                details={
                    "model": agent_info.get("model"),
                    "tools_count": agent_info.get("tools_count")
                }
            )
        else:
            components["agent"] = ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message="Agent service not initialized"
            )
            overall_status = HealthStatus.DEGRADED
    except Exception as e:
        components["agent"] = ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message=f"Agent service error: {str(e)}"
        )
        overall_status = HealthStatus.UNHEALTHY
    
    # Check FAISS service
    try:
        faiss_ready = faiss.is_ready()
        if faiss_ready:
            faiss_info = faiss.get_info()
            components["faiss"] = ComponentHealth(
                status=HealthStatus.HEALTHY,
                message="FAISS service operational",
                details={
                    "tool_name": faiss_info.get("tool_name"),
                    "cache_enabled": faiss_info.get("cache_enabled")
                }
            )
        else:
            components["faiss"] = ComponentHealth(
                status=HealthStatus.DEGRADED,
                message="FAISS service not initialized (optional)"
            )
            # FAISS is optional, so don't mark as unhealthy
    except Exception as e:
        components["faiss"] = ComponentHealth(
            status=HealthStatus.DEGRADED,
            message=f"FAISS service warning: {str(e)}"
        )
    
    # Check database
    try:
        customer_count = customer_db.get_customer_count()
        components["database"] = ComponentHealth(
            status=HealthStatus.HEALTHY,
            message="Database accessible",
            details={
                "crm_customers": customer_count,
                "database_path": str(settings.crm_database_full_path)
            }
        )
    except Exception as e:
        components["database"] = ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message=f"Database error: {str(e)}"
        )
        overall_status = HealthStatus.UNHEALTHY
    
    return HealthResponse(
        status=overall_status,
        components=components,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@router.get(
    "/tools",
    response_model=ToolsResponse,
    summary="List Available Tools",
    description="""
    Get information about all tools available to the agent.
    
    Tools include:
    - Search tools (Wikipedia, ArXiv, DuckDuckGo)
    - CRM database tools (business client queries)
    - SQL query tool (Chinook music database)
    - FAISS retriever (LangSmith documentation)
    """,
    responses={
        200: {"model": ToolsResponse, "description": "List of tools"}
    }
)
async def list_tools(agent: AgentServiceDep) -> ToolsResponse:
    """
    List all available tools
    
    Args:
        agent: Agent service dependency
        
    Returns:
        ToolsResponse with tool information
    """
    try:
        tools_info = agent.get_tools_info()
        
        tools = [
            ToolInfo(name=tool["name"], description=tool["description"])
            for tool in tools_info
        ]
        
        return ToolsResponse(
            tools=tools,
            total=len(tools)
        )
        
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tools: {str(e)}"
        )
