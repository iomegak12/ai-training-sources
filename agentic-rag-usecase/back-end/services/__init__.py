"""
Services package for Agentic RAG API
Provides FAISS and Agent singleton services
"""
from .faiss_service import faiss_service, FAISSService
from .agent_service import agent_service, AgentService

__all__ = [
    'faiss_service',
    'FAISSService',
    'agent_service',
    'AgentService'
]
