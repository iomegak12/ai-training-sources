"""
API Request and Response Models
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class MessageRole(str, Enum):
    """Message role for conversation history"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """Single message in conversation history"""
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is LangSmith?"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=10000, description="User message/question")
    conversation_history: Optional[List[ConversationMessage]] = Field(
        default=None,
        description="Previous conversation messages for context"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is LangSmith?",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Hello"
                    },
                    {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    }
                ]
            }
        }


class AgentStep(BaseModel):
    """Individual step in agent reasoning"""
    type: str = Field(..., description="Step type: 'agent' or 'tool'")
    content: Dict[str, Any] = Field(..., description="Step content/data")


class ChatResponse(BaseModel):
    """Response model for chat endpoint (blocking)"""
    message: str = Field(..., description="Assistant's response message")
    conversation_history: List[ConversationMessage] = Field(
        ..., 
        description="Complete conversation history including this response"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata about the response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "LangSmith is a platform for building production-grade LLM applications.",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "What is LangSmith?"
                    },
                    {
                        "role": "assistant",
                        "content": "LangSmith is a platform for building production-grade LLM applications."
                    }
                ],
                "metadata": {
                    "tools_used": ["langsmith_search"],
                    "response_time_ms": 1234
                }
            }
        }


class StreamEventType(str, Enum):
    """Types of streaming events"""
    START = "start"
    AGENT = "agent"
    TOOL = "tool"
    END = "end"
    ERROR = "error"


class StreamEvent(BaseModel):
    """Streaming event for chat-stream endpoint"""
    event: StreamEventType = Field(..., description="Type of streaming event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event": "agent",
                "data": {
                    "messages": [
                        {
                            "type": "ai",
                            "content": "I'll search for information about LangSmith."
                        }
                    ]
                }
            }
        }


class HealthStatus(str, Enum):
    """Health check statuses"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status of individual component"""
    status: HealthStatus = Field(..., description="Component health status")
    message: Optional[str] = Field(default=None, description="Status message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details")


class HealthResponse(BaseModel):
    """Response model for health endpoint"""
    status: HealthStatus = Field(..., description="Overall system health status")
    components: Dict[str, ComponentHealth] = Field(
        ..., 
        description="Health status of individual components"
    )
    version: Optional[str] = Field(default="1.0.0", description="API version")
    timestamp: Optional[str] = Field(default=None, description="Health check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "components": {
                    "agent": {
                        "status": "healthy",
                        "message": "Agent service operational"
                    },
                    "faiss": {
                        "status": "healthy",
                        "message": "FAISS service operational"
                    },
                    "database": {
                        "status": "healthy",
                        "message": "Databases accessible"
                    }
                }
            }
        }


class ToolInfo(BaseModel):
    """Information about an available tool"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "WikipediaSearch",
                "description": "Search for information on Wikipedia by terms, keywords or topics"
            }
        }


class ToolsResponse(BaseModel):
    """Response model for tools endpoint"""
    tools: List[ToolInfo] = Field(..., description="List of available tools")
    total: int = Field(..., description="Total number of tools")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 10,
                "tools": [
                    {
                        "name": "WikipediaSearch",
                        "description": "Search for information on Wikipedia"
                    },
                    {
                        "name": "ArxivSearch",
                        "description": "Search for academic papers on ArXiv"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "Message cannot be empty",
                "status_code": 400
            }
        }
