"""
API package for Agentic RAG API
FastAPI routes, models, and dependencies
"""
from .routes import router
from .models import ChatRequest, ChatResponse, HealthResponse, ToolsResponse
from .dependencies import get_agent_service, get_faiss_service, get_customer_manager

__all__ = [
    'router',
    'ChatRequest',
    'ChatResponse',
    'HealthResponse',
    'ToolsResponse',
    'get_agent_service',
    'get_faiss_service',
    'get_customer_manager'
]
