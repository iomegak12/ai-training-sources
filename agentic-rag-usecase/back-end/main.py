"""
Agentic RAG REST API
Main application entry point with FastAPI
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config.settings import settings
from config.logging_config import setup_logging, get_logger
from api.routes import router
from api.middleware import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    RequestLoggingMiddleware
)
from db.init_databases import initialize_databases
from services.agent_service import agent_service
from services.faiss_service import faiss_service


# Setup logging
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    log_file_enabled=settings.log_file_enabled,
    log_file_path=settings.log_file_path
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown
    
    Startup:
    - Initialize databases
    - Initialize FAISS service
    - Initialize agent service
    
    Shutdown:
    - Clean up resources
    """
    # Startup
    logger.info("=" * 70)
    logger.info("AGENTIC RAG API - STARTUP")
    logger.info("=" * 70)
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        errors = settings.validate_on_startup()
        if errors:
            logger.warning(f"Configuration warnings: {len(errors)}")
            for error in errors:
                logger.warning(f"  - {error}")
        
        # Initialize databases
        logger.info("\nInitializing databases...")
        db_results = initialize_databases(crm_sample_records=25)
        
        # Initialize FAISS service (optional - continues if fails)
        logger.info("\nInitializing FAISS service...")
        try:
            faiss_service.initialize()
        except Exception as e:
            logger.warning(f"FAISS initialization failed (continuing without it): {str(e)}")
        
        # Initialize agent service
        logger.info("\nInitializing agent service...")
        agent_success = agent_service.initialize()
        
        if not agent_success:
            logger.error("Failed to initialize agent service!")
            raise RuntimeError("Agent service initialization failed")
        
        logger.info("\n" + "=" * 70)
        logger.info("STARTUP COMPLETE ✓")
        logger.info(f"API Server: http://{settings.api_host}:{settings.api_port}")
        logger.info(f"Documentation: http://{settings.api_host}:{settings.api_port}{settings.docs_url}")
        logger.info("=" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("\n" + "=" * 70)
    logger.info("AGENTIC RAG API - SHUTDOWN")
    logger.info("=" * 70)
    logger.info("Cleaning up resources...")
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Agentic RAG REST API",
    description="""
    Multi-tool agentic RAG system with LangGraph ReAct agent.
    
    ## Features
    
    - **Multiple Search Tools**: Wikipedia, ArXiv, DuckDuckGo
    - **CRM Database**: Business client queries and analytics
    - **SQL Analytics**: Natural language queries on Chinook music database
    - **FAISS RAG**: Vector-based retrieval for LangSmith documentation
    - **Streaming Support**: Real-time agent reasoning and tool use
    
    ## Endpoints
    
    - `POST /chat` - Synchronous chat (full response)
    - `POST /chat-stream` - Streaming chat (Server-Sent Events)
    - `GET /health` - Health check for all components
    - `GET /tools` - List available tools
    
    ## Authentication
    
    No authentication required (development mode).
    """,
    version="1.0.0",
    docs_url=settings.docs_url if settings.docs_enabled else None,
    redoc_url=settings.redoc_url if settings.docs_enabled else None,
    openapi_url=settings.openapi_url if settings.docs_enabled else None,
    lifespan=lifespan
)

# Exception handlers (must be registered before middleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
logger.info("Exception handlers registered")

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)
logger.info("Request logging middleware enabled")

# CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {settings.cors_origins_list}")

# Rate limiting
if settings.rate_limit_enabled:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info(f"Rate limiting enabled: {settings.rate_limit_per_minute}/min, {settings.rate_limit_per_hour}/hour")

# Include routes
app.include_router(router, prefix="", tags=["Agentic RAG"])


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs"""
    return JSONResponse(
        content={
            "message": "Agentic RAG REST API",
            "version": "1.0.0",
            "docs": f"http://{settings.api_host}:{settings.api_port}{settings.docs_url}",
            "health": f"http://{settings.api_host}:{settings.api_port}/health"
        }
    )


def main():
    """Main entry point for running the server"""
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers if not settings.api_reload else 1,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
