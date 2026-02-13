"""
API Dependencies
Dependency injection for FastAPI endpoints
"""
from fastapi import Depends, HTTPException, status
from typing import Annotated
from services.agent_service import agent_service, AgentService
from services.faiss_service import faiss_service, FAISSService
from db.manager import CustomerManager
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


def get_agent_service() -> AgentService:
    """
    Get initialized agent service
    
    Returns:
        AgentService instance
        
    Raises:
        HTTPException: If agent service is not initialized
    """
    if not agent_service.is_ready():
        logger.info("Agent service not initialized, initializing now...")
        success = agent_service.initialize()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent service initialization failed"
            )
    
    return agent_service


def get_faiss_service() -> FAISSService:
    """
    Get initialized FAISS service
    
    Returns:
        FAISSService instance
        
    Raises:
        HTTPException: If FAISS service is not initialized
    """
    if not faiss_service.is_ready():
        logger.info("FAISS service not initialized, initializing now...")
        success = faiss_service.initialize()
        if not success:
            logger.warning("FAISS service initialization failed, agent will work without FAISS tool")
    
    return faiss_service


def get_customer_manager() -> CustomerManager:
    """
    Get CustomerManager instance for CRM database
    
    Returns:
        CustomerManager instance
    """
    db_path = settings.crm_database_full_path
    db_uri = f"sqlite:///{db_path}"
    return CustomerManager(db_uri)


# Type aliases for dependency injection
AgentServiceDep = Annotated[AgentService, Depends(get_agent_service)]
FAISSServiceDep = Annotated[FAISSService, Depends(get_faiss_service)]
CustomerManagerDep = Annotated[CustomerManager, Depends(get_customer_manager)]
