"""Request models for API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """Request model for the query endpoint."""
    
    question: str = Field(
        ...,
        description="The question to ask the AI agent",
        min_length=1,
        max_length=2000,
        examples=["What is LangSmith?"]
    )
    
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum number of tokens in the response (overrides default)",
        ge=1,
        le=4000
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Temperature for response generation (overrides default)",
        ge=0.0,
        le=2.0
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Tell me about LangSmith",
                "max_tokens": 2000,
                "temperature": 0.1
            }
        }
