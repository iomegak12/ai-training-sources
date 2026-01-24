"""Response models for API endpoints."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryResponse(BaseModel):
    """Response model for the query endpoint."""
    
    question: str = Field(..., description="The original question asked")
    answer: str = Field(..., description="The AI-generated answer")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used to answer the question")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp of the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is LangSmith?",
                "answer": "LangSmith is a platform for building production-grade LLM applications...",
                "tools_used": ["langsmith_search"],
                "timestamp": "2025-11-13T12:00:00.000000"
            }
        }


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""
    
    status: str = Field(..., description="Health status of the service")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp of the health check")
    version: str = Field(..., description="API version")
    vector_db_initialized: bool = Field(..., description="Whether the vector database is initialized")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-13T12:00:00.000000",
                "version": "1.0.0",
                "vector_db_initialized": True
            }
        }


class ToolInfo(BaseModel):
    """Information about a single tool."""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "GoogleSearch",
                "description": "Search the internet for real-time information"
            }
        }


class ToolsResponse(BaseModel):
    """Response model for the tools endpoint."""
    
    tools: List[ToolInfo] = Field(..., description="List of available tools")
    count: int = Field(..., description="Total number of available tools")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tools": [
                    {"name": "GoogleSearch", "description": "Search the internet for real-time information"},
                    {"name": "WikipediaSearch", "description": "Search Wikipedia for encyclopedic information"}
                ],
                "count": 2
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Detailed error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp of the error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Question must not be empty",
                "status_code": 400,
                "timestamp": "2025-11-13T12:00:00.000000"
            }
        }
